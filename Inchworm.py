#! python 3
import clr
clr.AddReference("Eto")
clr.AddReference("Rhino.UI")

import Rhino
import Eto.Drawing as drawing
import Eto.Forms as forms


UNITS_TO_METERS = {
    "Millimeters (mm)": 0.001,
    "Centimeters (cm)": 0.01,
    "Meters (m)":       1.0,
    "Inches (in)":      0.0254,
    "Feet (ft)":        0.3048,
}

PRESET_SCALES = [
    ("1:50",   1, 50),
    ("1:100",  1, 100),
    ("1:200",  1, 200),
    ("1:500",  1, 500),
    ("1:1000", 1, 1000),
]

MAX_HISTORY_ENTRIES = 8
COLOR_INVALID = drawing.Color.FromArgb(255, 100, 100)


def make_label(text, gray=False):
    label = forms.Label()
    label.Text = text
    label.VerticalAlignment = forms.VerticalAlignment.Center
    if gray:
        label.Font = drawing.SystemFonts.Default()
        label.TextColor = drawing.Colors.Gray
    return label


def make_textbox(initial_text, width=140):
    textbox = forms.TextBox()
    textbox.Text = initial_text
    textbox.Size = drawing.Size(width, 25)
    return textbox


def make_dropdown(items, selected_index):
    dropdown = forms.DropDown()
    dropdown.DataStore = items
    dropdown.SelectedIndex = selected_index
    dropdown.Size = drawing.Size(160, 25)
    return dropdown


def make_button(text, width=90, height=27):
    button = forms.Button()
    button.Text = text
    button.Size = drawing.Size(width, height)
    return button


def format_number(value):
    return f"{value:.4f}".rstrip("0").rstrip(".")


def extract_unit_abbreviation(unit_label):
    return unit_label[unit_label.index("(") + 1 : unit_label.index(")")]


class InchwormDialog(forms.Dialog):

    def __init__(self):
        super().__init__()
        self.Title = "Inchworm"
        self.ClientSize = drawing.Size(560, 470)
        self.Resizable = False
        self.is_updating = False
        self.final_output = None
        self.session_history = []

        self._build_widgets()
        self._build_layout()
        self._bind_events()
        self._refresh_output_label()

    def _build_widgets(self):
        unit_keys = list(UNITS_TO_METERS.keys())

        self.scale_numerator_tb   = make_textbox("1", width=60)
        self.scale_denominator_tb = make_textbox("0", width=60)
        self.real_length_tb       = make_textbox("0", width=130)
        self.model_length_tb      = make_textbox("0", width=130)
        self.real_unit_dd         = make_dropdown(unit_keys, selected_index=2)
        self.model_unit_dd        = make_dropdown(unit_keys, selected_index=0)

        self.direction_label = forms.Label()
        self.direction_label.Text      = "▼  Real → Model"
        self.direction_label.TextColor = drawing.Colors.DarkBlue

        self.output_label = forms.Label()
        self.output_label.Text = "Ratio 1:0 | Real: 0 m | Model: 0 mm"
        self.output_label.Font = drawing.SystemFonts.Bold(10)

        self.apply_button = make_button("Copy & Log", width=110, height=30)
        self.apply_button.Click += self._on_apply_clicked

        self.swap_button = make_button("⇅ Swap", width=80, height=30)
        self.swap_button.Click += self._on_swap_clicked

        self.close_button = make_button("Close", width=80, height=30)
        self.close_button.Click += lambda s, e: self.Close()

        self.history_listbox = forms.ListBox()
        self.history_listbox.Size = drawing.Size(520, 110)

        self.preset_buttons = []
        for label_text, num, den in PRESET_SCALES:
            btn = make_button(label_text, width=72, height=25)
            btn.Tag = (num, den)
            btn.Click += self._on_preset_clicked
            self.preset_buttons.append(btn)

    def _build_layout(self):
        layout = forms.PixelLayout()

        layout.Add(make_label("Scale Ratio"),       20,  22)
        layout.Add(self.scale_numerator_tb,        140,  20)
        layout.Add(make_label(" : "),              204,  22)
        layout.Add(self.scale_denominator_tb,      220,  20)

        layout.Add(make_label("Presets:"),          20,  60)
        x_offset = 90
        for btn in self.preset_buttons:
            layout.Add(btn, x_offset, 57)
            x_offset += 78

        layout.Add(self.direction_label,            20,  98)

        layout.Add(make_label("Real-World Length"), 20, 133)
        layout.Add(self.real_length_tb,            160, 131)
        layout.Add(self.real_unit_dd,              298, 131)

        layout.Add(make_label("Model Length"),      20, 178)
        layout.Add(self.model_length_tb,           160, 176)
        layout.Add(self.model_unit_dd,             298, 176)

        layout.Add(self.swap_button,                20, 223)
        layout.Add(self.apply_button,              110, 223)
        layout.Add(self.close_button,              228, 223)

        layout.Add(self.output_label,               20, 268)

        layout.Add(make_label("Session History:"),  20, 303)
        layout.Add(self.history_listbox,            20, 323)

        layout.Add(make_label(
            "Modify Real or Model — the other updates automatically.  |  Enter = Copy & Log",
            gray=True), 20, 448)

        self.Content = layout

    def _bind_events(self):
        self.scale_numerator_tb.TextChanged        += lambda s, e: self._recalculate(from_real=True)
        self.scale_denominator_tb.TextChanged      += lambda s, e: self._recalculate(from_real=True)
        self.real_length_tb.TextChanged            += lambda s, e: self._recalculate(from_real=True)
        self.real_unit_dd.SelectedIndexChanged     += lambda s, e: self._recalculate(from_real=True)
        self.model_length_tb.TextChanged           += lambda s, e: self._recalculate(from_real=False)
        self.model_unit_dd.SelectedIndexChanged    += lambda s, e: self._recalculate(from_real=True)
        self.KeyDown                               += self._on_key_down

    def _on_key_down(self, sender, e):
        if str(e.Key) == "Enter":
            self._on_apply_clicked(sender, e)

    def _parse_ratio(self):
        numerator   = float(self.scale_numerator_tb.Text)
        denominator = float(self.scale_denominator_tb.Text)
        if numerator == 0 or denominator == 0:
            raise ValueError("Ratio parts must be non-zero.")
        return numerator / denominator

    def _to_meters(self, text, unit_dropdown):
        return float(text) * UNITS_TO_METERS[unit_dropdown.SelectedValue]

    def _from_meters(self, value_in_meters, unit_dropdown):
        return value_in_meters / UNITS_TO_METERS[unit_dropdown.SelectedValue]

    def _set_field_state(self, textbox, valid):
        if valid:
            textbox.BackgroundColor = drawing.Colors.Transparent
        else:
            textbox.BackgroundColor = COLOR_INVALID

    def _update_direction_indicator(self, from_real):
        if from_real:
            self.direction_label.Text      = "▼  Real → Model"
            self.direction_label.TextColor = drawing.Colors.DarkBlue
        else:
            self.direction_label.Text      = "▲  Model → Real"
            self.direction_label.TextColor = drawing.Colors.DarkGreen

    def _recalculate(self, from_real):
        if self.is_updating:
            return
        self.is_updating = True
        self._update_direction_indicator(from_real)
        active_field = self.real_length_tb if from_real else self.model_length_tb
        try:
            ratio = self._parse_ratio()
            if from_real:
                real_in_meters = self._to_meters(self.real_length_tb.Text, self.real_unit_dd)
                self.model_length_tb.Text = format_number(
                    self._from_meters(real_in_meters * ratio, self.model_unit_dd)
                )
            else:
                model_in_meters = self._to_meters(self.model_length_tb.Text, self.model_unit_dd)
                self.real_length_tb.Text = format_number(
                    self._from_meters(model_in_meters / ratio, self.real_unit_dd)
                )
            self._set_field_state(active_field, valid=True)
        except ValueError:
            self._set_field_state(active_field, valid=False)
        self._refresh_output_label()
        self.is_updating = False

    def _refresh_output_label(self):
        try:
            real_value  = format_number(float(self.real_length_tb.Text))
            model_value = format_number(float(self.model_length_tb.Text))
            real_unit   = extract_unit_abbreviation(self.real_unit_dd.SelectedValue)
            model_unit  = extract_unit_abbreviation(self.model_unit_dd.SelectedValue)
            num = self.scale_numerator_tb.Text
            den = self.scale_denominator_tb.Text
            self.output_label.Text = (
                f"Ratio {num}:{den} | "
                f"Real: {real_value} {real_unit} | "
                f"Model: {model_value} {model_unit}"
            )
        except (ValueError, TypeError):
            self.output_label.Text = "Error: Check input values."

    def _on_preset_clicked(self, sender, event):
        self.scale_numerator_tb.Text   = str(sender.Tag[0])
        self.scale_denominator_tb.Text = str(sender.Tag[1])

    def _on_swap_clicked(self, sender, event):
        real_text  = self.real_length_tb.Text
        model_text = self.model_length_tb.Text
        real_idx   = self.real_unit_dd.SelectedIndex
        model_idx  = self.model_unit_dd.SelectedIndex

        self.is_updating = True
        self.real_length_tb.Text         = model_text
        self.model_length_tb.Text        = real_text
        self.real_unit_dd.SelectedIndex  = model_idx
        self.model_unit_dd.SelectedIndex = real_idx
        self.is_updating = False

        self._recalculate(from_real=True)

    def _add_to_history(self, entry):
        self.session_history.insert(0, entry)
        if len(self.session_history) > MAX_HISTORY_ENTRIES:
            self.session_history.pop()
        self.history_listbox.DataStore = list(self.session_history)

    def _on_apply_clicked(self, sender, event):
        output = self.output_label.Text
        if "Error" in output:
            return
        self.final_output = output
        self._add_to_history(self.final_output)
        Rhino.RhinoApp.WriteLine(f"Inchworm Result: {self.final_output}")
        forms.Clipboard().Text = self.final_output


if __name__ == "__main__":
    dialog = InchwormDialog()
    dialog.Topmost = True
    dialog.ShowModal(Rhino.UI.RhinoEtoApp.MainWindow)