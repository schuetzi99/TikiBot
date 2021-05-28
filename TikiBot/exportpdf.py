try:  # Python 2
    from Tkinter import *  # noqa
except ImportError:  # Python 3
    from tkinter import *  # noqa

from fpdf import FPDF
from recipes import Recipe
import os

class ExportPdf(FPDF):

    def header(self):
        #self.add_font('sysfont', '', r"/usr/share/fonts/truetype/Data70.ttf", uni=True)
        self.image('resources/images/lhm-logo.png', 170, 8, 33)
        # Arial bold 15
        self.set_font('Arial', 'B', 15)
        # Move to the right
        self.cell(80)
        # Title
        self.cell(50, 10, 'Let-Him-Mix', 1, 0, 'C')
        # Line break
        self.ln(20)

    # Page footer
    def footer(self):
        # Position at 1.5 cm from bottom
        self.set_y(-15)
        # Arial italic 8
        self.set_font('Arial', 'I', 13)
        # Page number
        self.multi_cell(0, 5, 'Seite ' + str(self.page_no()) + '/{nb}' + '\nwww.let-him-mix.de', 0, 'C')

    def exportpdf(self):
        #header()
        #footer()
        self.pdf = ExportPdf()
        #recipes = Recipe(self)
        self.pdf.alias_nb_pages()
        self.pdf.add_page()
        self.pdf.set_auto_page_break(0)
        height_of_cell = 5
        page_height = 295
        bottom_margin = 15
        self.pdf.set_font('Times', '', 12)
        types = Recipe.getTypeNames()
        for type_ in types:
            if type_ != 'Extra Schuss':
                self.pdf.set_font('Times', '', 22)
                space_left=page_height-(self.pdf.get_y()+bottom_margin) # space left on page
                if (height_of_cell * 6 > space_left):
                    self.pdf.add_page() # page break
                currentrecipes = Recipe.getRecipesByType(type_)
                number_recipes = 0
                for recipe in currentrecipes:
                    if Recipe.canMake(recipe):
                        number_recipes += 1
                self.pdf.cell(60, 18, type_ + " (" + str(number_recipes) + ")", 0,1, 'C')
                for recipe in currentrecipes:
                    if Recipe.canMake(recipe):
                        name = recipe.getName()
                        apbv = Recipe.getAlcoholPercentByVolume(recipe)
                        if apbv < 0.1:
                            name=name + ' (Alkoholfrei)'
                        else:
                            #alc_warn = "\u2620" * int(100*apbv/100.0/14.0)
                            #alc_warn = "@" * int(100*apbv/100.0/14.0)
                            name = name + " (%.1f%% Alcoholgehalt)" % (apbv)
                            #name = name + " (%.1f%% Volumen-Alcoholgehalt  %s)" % (apbv, alc_warn)
                        self.pdf.set_font('Times', '', 14)
                        space_left=page_height-(self.pdf.get_y()+bottom_margin) # space left on page
                        if (height_of_cell * 2 > space_left):
                            self.pdf.add_page() # page break
                        self.pdf.cell(90, 5, name, 'B',2)
                        self.pdf.cell(10, 5, '         ', 0, 0)
                        currenting=[]
                        for ing in recipe.ingredients:
                            currenting.append(ing.readableDesc())
                            #currenting.append(ing.readableDesc(partial, metric=True))
                        self.pdf.set_font('Times', '', 13)
                        self.pdf.cell(50, 5, ', '.join(currenting), 0, 0)
                        self.pdf.cell(0, 7, '', 0, 1)
        self.pdf.output(os.path.expanduser("~/cocktailkarte.pdf"), 'F')
