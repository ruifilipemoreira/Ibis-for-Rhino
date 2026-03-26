#! python 3
import clr
clr.AddReference("Eto")
clr.AddReference("Rhino.UI")

import Rhino
import Eto.Drawing as drawing
import Eto.Forms as forms

class InteractiveScaleForm(forms.Dialog):
    def __init__(self):
        super().__init__()
        self.Title = "Inchworm"
        
        self.ClientSize = drawing.Size(540, 300) 
        self.Resizable = False 
        
        self.units = {
            "Millimeters (mm)": 0.001, 
            "Centimeters (cm)": 0.01, 
            "Meters (m)": 1.0, 
            "Inches (in)": 0.0254, 
            "Feet (ft)": 0.3048
        }
        self.unit_keys = list(self.units.keys())
        self.is_updating = False
        
        self.final_output = None 
        
        lbl_scale = forms.Label()
        lbl_scale.Text = "Scale Ratio"
        lbl_scale.VerticalAlignment = forms.VerticalAlignment.Center
        
        self.scale_num_tb = forms.TextBox()
        self.scale_num_tb.Text = "1"
        self.scale_num_tb.Size = drawing.Size(70, 25)
        
        lbl_colon = forms.Label()
        lbl_colon.Text = " : "
        lbl_colon.VerticalAlignment = forms.VerticalAlignment.Center
        
        self.scale_den_tb = forms.TextBox()
        self.scale_den_tb.Text = "0"
        self.scale_den_tb.Size = drawing.Size(70, 25)
        
        lbl_real = forms.Label()
        lbl_real.Text = "Real-World Length"
        lbl_real.VerticalAlignment = forms.VerticalAlignment.Center
        
        self.real_tb = forms.TextBox()
        self.real_tb.Text = "0"
        self.real_tb.Size = drawing.Size(165, 25)
        
        self.real_unit_dd = forms.DropDown()
        self.real_unit_dd.DataStore = self.unit_keys
        self.real_unit_dd.SelectedIndex = 2
        self.real_unit_dd.Size = drawing.Size(180, 25)
        
        lbl_model = forms.Label()
        lbl_model.Text = "Model Length"
        lbl_model.VerticalAlignment = forms.VerticalAlignment.Center
        
        self.model_tb = forms.TextBox()
        self.model_tb.Text = "0"
        self.model_tb.Size = drawing.Size(165, 25)
        
        self.model_unit_dd = forms.DropDown()
        self.model_unit_dd.DataStore = self.unit_keys
        self.model_unit_dd.SelectedIndex = 0
        self.model_unit_dd.Size = drawing.Size(180, 25)
        
        self.apply_btn = forms.Button()
        self.apply_btn.Text = "Copy & Log"
        self.apply_btn.Size = drawing.Size(100, 30)
        self.apply_btn.Click += self.on_apply_click

        self.output_lbl = forms.Label()
        self.output_lbl.Text = "Ratio 1:0 | Real: 0 m | Model: 0 mm"
        self.output_lbl.Font = drawing.SystemFonts.Bold(10)

        lbl_instr1 = forms.Label()
        lbl_instr1.Text = "Instructions: Set Ratio and modify Real or Model lengths to calculate."
        lbl_instr1.Font = drawing.SystemFonts.Default()
        lbl_instr1.TextColor = drawing.Colors.Gray

        lbl_instr2 = forms.Label()
        lbl_instr2.Text = "Click 'Copy & Log' to send the result to the clipboard and command line."
        lbl_instr2.Font = drawing.SystemFonts.Default()
        lbl_instr2.TextColor = drawing.Colors.Gray
        
        layout = forms.PixelLayout()
        layout.Add(lbl_scale, 20, 22)
        layout.Add(self.scale_num_tb, 140, 20)
        layout.Add(lbl_colon, 215, 22)
        layout.Add(self.scale_den_tb, 235, 20)
        
        layout.Add(lbl_real, 20, 67)
        layout.Add(self.real_tb, 140, 65)
        layout.Add(self.real_unit_dd, 315, 65)
        
        layout.Add(lbl_model, 20, 112)
        layout.Add(self.model_tb, 140, 110)
        layout.Add(self.model_unit_dd, 315, 110)
        
        layout.Add(self.apply_btn, 20, 175)
        layout.Add(self.output_lbl, 135, 180)

        layout.Add(lbl_instr1, 20, 230)
        layout.Add(lbl_instr2, 20, 250)
        
        self.Content = layout
        
        self.scale_num_tb.TextChanged += self.calc_from_real
        self.scale_den_tb.TextChanged += self.calc_from_real
        self.real_tb.TextChanged += self.calc_from_real
        self.real_unit_dd.SelectedIndexChanged += self.calc_from_real
        self.model_tb.TextChanged += self.calc_from_model
        self.model_unit_dd.SelectedIndexChanged += self.calc_from_real
        self.update_label()

    def extract_abbr(self, unit_str):
        return unit_str.split("(")[1].replace(")", "") if "(" in unit_str else unit_str

    def format_number(self, val):
        s = "{:.4f}".format(val)
        return s.rstrip('0').rstrip('.') if '.' in s else s

    def update_label(self):
        try:
            num, den = self.scale_num_tb.Text, self.scale_den_tb.Text
            real_val = self.format_number(float(self.real_tb.Text))
            real_unit = self.extract_abbr(self.real_unit_dd.SelectedValue)
            model_val = self.format_number(float(self.model_tb.Text))
            model_unit = self.extract_abbr(self.model_unit_dd.SelectedValue)
            self.output_lbl.Text = "Ratio {}:{} | Real: {} {} | Model: {} {}".format(
                num, den, real_val, real_unit, model_val, model_unit)
        except:
            self.output_lbl.Text = "Error: Check input values."

    def calc_from_real(self, sender, e):
        if self.is_updating: return
        self.is_updating = True
        try:
            n, d = float(self.scale_num_tb.Text), float(self.scale_den_tb.Text)
            if d != 0: 
                ratio = n / d
                val = float(self.real_tb.Text) * self.units[self.real_unit_dd.SelectedValue]
                self.model_tb.Text = self.format_number((val * ratio) / self.units[self.model_unit_dd.SelectedValue])
        except ValueError: pass
        self.update_label()
        self.is_updating = False

    def calc_from_model(self, sender, e):
        if self.is_updating: return
        self.is_updating = True
        try:
            n, d = float(self.scale_num_tb.Text), float(self.scale_den_tb.Text)
            if n != 0 and d != 0:
                ratio = n / d
                val = float(self.model_tb.Text) * self.units[self.model_unit_dd.SelectedValue]
                self.real_tb.Text = self.format_number((val / ratio) / self.units[self.real_unit_dd.SelectedValue])
        except ValueError: pass
        self.update_label()
        self.is_updating = False

    def on_apply_click(self, sender, e):
        self.apply_btn.Enabled = False
        self.final_output = self.output_lbl.Text
        self.Close()

if __name__ == "__main__":
    dialog = InteractiveScaleForm()
    
    dialog.Topmost = True 
    
    dialog.ShowModal(Rhino.UI.RhinoEtoApp.MainWindow)
    
    if hasattr(dialog, 'final_output') and dialog.final_output:
        Rhino.RhinoApp.WriteLine("Inchworm Result: {}".format(dialog.final_output))
        cb = forms.Clipboard()
        cb.Text = dialog.final_output