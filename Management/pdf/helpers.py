from Management.templatetags.management_extras import commaise
from styles import *
from reportlab.platypus import Paragraph

class Row:
    __slots__ = ('cells', 'height')
    
    def __init__(self, cells = [], height = 15):
        self.cells = cells
        self.height = height
    def __len__(self):
        return self.cells.__len__()
    def __iter__(self):
        return self.cells.__iter__()

class Col:
    __slots__ = ('name', 'title', 'width')
    
    def __init__(self, name, title, width):
        self.name, self.title, self.width = name, title, width

class Table:
    def __init__(self, cols = [], rows = []):
        self.cols, self.rows = cols, rows
    def row_heights(self):
        return [row.height for row in self.rows]
    def col_widths(self):
        return [col.width for col in self.cols]
    def __len__(self):
        return self.rows.__len__()
    def __iter__(self):
        return self.rows.__iter__()

class Builder:
    def __init__(self, items, fields):
        self.items = items
        self.fields = fields
        self.summarized_fields = [field.name for field in fields]
        
    def build(self):
        row_summaries = dict([(field_name, 0) for field_name in self.summarized_fields])
        
        cols = [Col(field.name, field.title, field.width) for field in self.fields]
        
        table = Table(cols = cols)
        
        table.rows.append([field.title for field in self.fields])
            
        for item in self.items:
            row = Row()
            cell_heights = []
            
            for field in self.fields:
                cell_value = field.format(item)
                cell_heights.append(field.get_height(item))
                
                if field.is_summarized:
                    row_summaries[field.name] += cell_value
                if field.is_commaised:
                    field_value = commaise(cell_value)
    
                row.cells.append(field_value)
                
            row.height = max(cell_heights)
            table.rows.append(row)
        
        if row_summaries:
            sum_row = []
            for field in self.fields:
                if field.is_summarized:
                    cell_value = Paragraph(commaise(row_summaries[field.name]), styleSumRow)
                    sum_row.append(cell_value)
                else:
                    sum_row.append('')
                    
            table.rows.append(sum_row)
        
        return table