from Management.templatetags.management_extras import commaise
from styles import *
from reportlab.platypus import Paragraph

class Row(object):
    __slots__ = ('cells', 'height')
    
    def __init__(self, cells = None, height = None):
        self.cells = cells or []
        self.height = height
    def __len__(self):
        return self.cells.__len__()
    def __iter__(self):
        return self.cells.__iter__()

class Col(object):
    __slots__ = ('name', 'title', 'width')
    
    def __init__(self, name, title, width):
        self.name, self.title, self.width = name, title, width

class Table(object):
    def __init__(self, cols = None, rows = None):
        self.cols, self.rows = cols or [], rows or []
    def row_heights(self):
        return [row.height for row in self.rows]
    def col_widths(self):
        return [col.width for col in self.cols]
    def cells(self):
        return [row.cells for row in self.rows]
    def __len__(self):
        return self.rows.__len__()
    def __iter__(self):
        return self.rows.__iter__()

class Builder(object):
    def __init__(self, items, fields):
        self.items = items
        self.fields = fields
        
    def build(self):
        row_summaries = dict([(field.name, 0) for field in self.fields if field.is_summarized])
        
        cols = [Col(field.name, field.title, field.width) for field in self.fields]
        
        if not cols:
            return Table()
        
        table = Table(cols = cols)
        
        title_row = Row(cells = [unicode(field.title) for field in self.fields])
        
        table.rows.append(title_row)
            
        for item in self.items:
            row = Row()
            cell_heights = []
            
            for field in self.fields:
                cell_value = field.format(item)
                cell_heights.append(field.get_height(item))
                
                if field.is_summarized:
                    row_summaries[field.name] += cell_value
                if field.is_commaised:
                    cell_value = commaise(cell_value)
    
                row.cells.append(cell_value)
                
            row.height = max(cell_heights)
            table.rows.append(row)
        
        if row_summaries:
            sum_row = Row()
            for field in self.fields:
                if field.is_summarized:
                    cell_value = Paragraph(commaise(row_summaries[field.name]), styleSumRow)
                    sum_row.cells.append(cell_value)
                else:
                    sum_row.cells.append('')
                    
            table.rows.append(sum_row)

        return table