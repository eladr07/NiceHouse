import settings, models
import logging
from datetime import datetime, date
from templatetags.management_extras import commaise
import reportlab.rl_config
reportlab.rl_config.warnOnMissingFontGlyphs = 0

from reportlab.lib.pagesizes import A4, landscape
from django.utils.translation import ugettext
from django.core.exceptions import ObjectDoesNotExist
from reportlab.pdfgen import canvas
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import Paragraph, SimpleDocTemplate, Image, Spacer, Frame, Table, PageBreak
from reportlab.platypus.tables import TableStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib import colors
from reportlab.lib.enums import *
from reportlab.lib.units import mm
from pyfribidi import log2vis

#register Hebrew fonts
pdfmetrics.registerFont(TTFont('David', settings.MEDIA_ROOT + 'fonts/DavidCLM-Medium.ttf'))
pdfmetrics.registerFont(TTFont('David-Bold', settings.MEDIA_ROOT + 'fonts/DavidCLM-Bold.ttf'))
pdfmetrics.registerFontFamily('David', normal='David', bold='David-Bold')
#template styles
styleN = ParagraphStyle('normal', fontName='David',fontSize=16, leading=15, alignment=TA_RIGHT)
styleNormal13 = ParagraphStyle('normal', fontName='David',fontSize=13, leading=15, alignment=TA_RIGHT)
styleDate = ParagraphStyle('date', fontName='David',fontSize=14, leading=15)
styleRow = ParagraphStyle('sumRow', fontName='David',fontSize=11, leading=15)
styleRow9 = ParagraphStyle('sumRow', fontName='David',fontSize=9, leading=15, alignment=TA_RIGHT)
styleSumRow = ParagraphStyle('Row', fontName='David-Bold',fontSize=11, leading=15)
styleSaleSumRow = ParagraphStyle('Row', fontName='David-Bold',fontSize=9, leading=15)
styleSubj = ParagraphStyle('subject', fontName='David',fontSize=16, leading=15, alignment=TA_CENTER)
styleSubTitleBold = ParagraphStyle('subtitle', fontName='David-Bold', fontSize=15, alignment=TA_CENTER)
styleSubTitle = ParagraphStyle('subtitle', fontName='David', fontSize=15, alignment=TA_CENTER)

saleTableStyle = TableStyle(
                            [('FONTNAME', (0,0), (-1,0), 'David-Bold'),
                             ('FONTNAME', (0,1), (-1,-1), 'David'),
                             ('FONTSIZE', (0,0), (-1,-1), 9),
                             ('ALIGN', (0,0), (-1,-1), 'CENTER'),
                             ('INNERGRID', (0,0), (-1,-1), 0.25, colors.black),
                             ('BOX', (0,0), (-1,-1), 0.25, colors.black),
                             ('LEFTPADDING', (0,0), (-1,-1), 8),
                             ('RIGHTPADDING', (0,0), (-1,-1), 8),
                             ]
                            )
nhsalariesTableStyle = TableStyle(
                            [('FONTNAME', (0,0), (-1,0), 'David-Bold'),
                             ('FONTNAME', (0,1), (-1,-1), 'David'),
                             ('FONTSIZE', (0,0), (-1,-1), 9),
                             ('ALIGN', (0,0), (-1,-1), 'CENTER'),
                             ('INNERGRID', (0,0), (-1,-1), 0.25, colors.black),
                             ('BOX', (0,0), (-1,-1), 0.25, colors.black),
                             ('LEFTPADDING', (0,0), (-1,-1), 8),
                             ('RIGHTPADDING', (0,0), (-1,-1), 8),
                             ]
                            )
salariesTableStyle = TableStyle(
                            [('FONTNAME', (0,0), (-1,1), 'David-Bold'),
                             ('FONTNAME', (0,2), (-1,-1), 'David'),
                             ('SPAN',(0,0),(5,0)),
                             ('SPAN',(6,0),(-1,0)),
                             ('FONTSIZE', (0,0), (-1,-1), 10),
                             ('ALIGN', (0,0), (-1,-1), 'CENTER'),
                             ('INNERGRID', (0,0), (-1,-1), 0.25, colors.black),
                             ('BOX', (0,0), (-1,-1), 0.25, colors.black),
                             ('LEFTPADDING', (0,0), (-1,-1), 8),
                             ('RIGHTPADDING', (0,0), (-1,-1), 8),
                             ]
                            )
projectTableStyle = TableStyle(
                               [('FONTNAME', (0,0), (-1,0), 'David-Bold'),
                                ('FONTNAME', (0,1), (-1,-1), 'David'),
                                ('FONTSIZE', (0,0), (-1,-1), 12),
                                ('ALIGN', (0,0), (-1,-1), 'CENTER'),
                                ('INNERGRID', (0,0), (-1,-1), 0.25, colors.black),
                                ('BOX', (0,0), (-1,-1), 0.25, colors.black),
                                ('LEFTPADDING', (0,0), (-1,-1), 8),
                                ('RIGHTPADDING', (0,0), (-1,-1), 8),
                                ]
                               )

def clientsPara(str):
    str2=''
    parts = str.strip().split('\r\n')
    parts.reverse()
    for s in parts:
        str2 += log2vis(s)
    return Paragraph(str2, ParagraphStyle('clients', fontName='David', fontSize=10, alignment=TA_CENTER))
def titlePara(str):
    '''
    returns a paragraph containing str with the subject style
    '''
    return Paragraph('<b><u>%s</u></b>' % log2vis(str), styleSubj)
def datePara():
    '''
    returns a paragraph containing date with the date style
    '''
    s = log2vis(u'תאריך : %s' % date.today().strftime('%d/%m/%Y'))
    return Paragraph('%s' % s, styleDate)
def tableCaption(caption=log2vis(u'ולהלן פירוט העסקאות')):
    return Paragraph(u'<u>%s</u>' % caption, 
                     ParagraphStyle(name='tableCaption', fontName='David-Bold', fontSize=15,
                                    alignment=TA_CENTER))
def nhLogo():
    return Image(settings.MEDIA_ROOT + 'images/nh_logo.jpg', 300, 50)
def sigPara():
    s = log2vis('ברגשי כבוד,') + '<br/>'
    s += log2vis('אלי בר-און')
    return Paragraph(s, ParagraphStyle(name='sig', fontName='David-Bold', fontSize=15,
                                       alignment=TA_LEFT))
def nhAddr():
    return Image(settings.MEDIA_ROOT + 'images/nh_addr.jpg', 300, 50)

class NumberedCanvas(canvas.Canvas):
    def __init__(self, *args, **kwargs):
        canvas.Canvas.__init__(self, *args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        """add page info to each page (page x of y)"""
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_number(num_pages)
            canvas.Canvas.showPage(self)
        canvas.Canvas.save(self)

    def draw_page_number(self, page_count):
        self.setFont("David", 13)
        self.drawRightString(40*mm, 20*mm,
                             log2vis(u"עמוד %d מתוך %d" % (self._pageNumber, page_count)))

class DocumentBase(object):
    def __init__(self):
        super(DocumentBase, self).__init__()
    def addLater(self, canv, doc):
        frame2 = Frame(0, 680, 650, 150)
        frame2.addFromList([nhLogo()], canv)
        frame4 = Frame(50, 20, 500, 70)
        frame4.addFromList([nhAddr()], canv)
        date_str = log2vis(u'תאריך : %s' % date.today().strftime('%d/%m/%Y'))
        canv.setFont('David',14)
        canv.drawRightString(50*mm, 275*mm, date_str)
    def addFirst(self, canv, doc):
        frame2 = Frame(0, 680, 650, 150)
        frame2.addFromList([nhLogo()], canv)
        frame4 = Frame(50, 20, 500, 70)
        frame4.addFromList([nhAddr()], canv)
        date_str = log2vis(u'תאריך : %s' % date.today().strftime('%d/%m/%Y'))
        canv.setFont('David',14)
        canv.drawRightString(50*mm, 275*mm, date_str)
    def build(self, filename):
        doc = SimpleDocTemplate(filename)
        doc.build(self.get_story(), self.addFirst, self.addLater, NumberedCanvas)
        return doc.canv
    def get_story(self):
        pass

class ProjectListWriter(DocumentBase):
    def __init__(self, projects):
        self.projects = projects

    def projectFlows(self):
        flows = [Paragraph(log2vis(u'נווה העיר - %s פרוייקטים' % len(self.projects)), styleSubTitleBold), Spacer(0,10)]
        headers = [log2vis(n) for n in [u'יזם',u'פרוייקט\nשם',u'עיר',u"בניינים\nמס'",u"דירות\nמס'",u'אנשי מכירות',u'אנשי קשר']]
        colWidths = [None,70,None,None,None,150,150]
        
        colWidths.reverse()
        headers.reverse()
        rows=[]

        for project in self.projects:

            if project.details != None:
                houses_num, buildings_num = project.details.houses_num, project.details.buildings_num
            else:
                houses_num, buildings_num = '---','---'
                
            row = [log2vis(project.initiator), log2vis(project.name), log2vis(project.city), buildings_num, houses_num]

            employees = ''
            for employee in project.employees.all():
                employee_str = unicode(employee)
                if employee.cell_phone:
                    employee_str += ' - ' + employee.cell_phone
                employees += log2vis(employee_str) + '<br/>'
                    
            contacts = ''
            if project.demand_contact:
                contact_str = u'תשלום: ' + unicode(project.demand_contact)
                if project.demand_contact.phone:
                    contact_str += ' - ' + project.demand_contact.phone
                contacts += log2vis(contact_str) + '<br/>'
            if project.payment_contact:
                contact_str = u"צ'קים: " + unicode(project.payment_contact)
                if project.payment_contact.phone:
                    contact_str += ' - ' + project.payment_contact.phone
                contacts += log2vis(contact_str) + '<br/>'                
            for contact in project.contacts.all():
                contact_str = unicode(contact)
                if contact.phone:
                    contact_str += ' - ' + contact.phone
                contacts += log2vis(contact_str) + '<br/>' 
            
            row.extend([Paragraph(employees, styleRow9), Paragraph(contacts, styleRow9)])

            row.reverse()
            rows.append(row)
            
        data = [headers]
        data.extend(rows)
        t = Table(data,colWidths, style = saleTableStyle, repeatRows = 1)
        flows.append(t)

        return flows
    
    def get_story(self):
        story = [Spacer(0,40)]
        story.append(titlePara(u'מצבת פרוייקטים'))
        story.append(Spacer(0, 10))
        story.extend(self.projectFlows())
        return story

class EmployeeListWriter(DocumentBase):

    def __init__(self, employees, nhemployees):
        self.employees = employees
        self.nhemployees = nhemployees

    def employeeFlows(self):
        #generate phones string for an employee
        def get_phones(employee):
            phones = ''
            for attr in ['work_phone','work_fax','cell_phone','home_phone','mate_phone']:
                attr_value = getattr(e, attr)
                if attr_value:
                    phones += '<u>' + log2vis(ugettext(attr)) + '</u><br/>'
                    phones += log2vis(attr_value) + '<br/>'
            return phones
        def get_account_str(employee):
            account = employee.account
            account_str = ''
            if account:
                account_str += '<u>' + log2vis(ugettext('payee')) + '</u><br/>'
                account_str += log2vis(account.payee) + '<br/>'
                account_str += '<u>' + log2vis(ugettext('bank')) + '</u><br/>'
                account_str += log2vis(account.bank) + '<br/>'
                account_str += '<u>' + log2vis(ugettext('branch')) + '</u><br/>'
                account_str += log2vis(u'%s %s' % (account.branch, account.branch_num)) + '<br/>'
                account_str += '<u>' + log2vis(ugettext('account_num')) + '</u><br/>'
                account_str += str(account.num) + '<br/>'
            return account_str            
            
        flows=[Paragraph(log2vis(u'נווה העיר - %s עובדים' % len(self.employees)), styleSubTitleBold),
               Spacer(0,10)]

        headers = [log2vis(name) for name in [u'מס"ד',u'פרטי\nשם',u'משפחה\nשם',u'טלפון',u'דוא"ל',u'כתובת',u'העסקה\nתחילת',u'העסקה\nסוג',u'חשבון\nפרטי',u'פרוייקטים']]
        colWidths = [None,None,None,85,90,70,None,None,60,80]
        
        headers.reverse()
        colWidths.reverse()
        
        rows = []
        rank = None
        for e in self.employees:
            if rank != e.rank:
                row = [log2vis(unicode(e.rank)),None,None,None,None]
                row.reverse()
                rows.append(row)
                rank = e.rank
            
            row=[e.id, log2vis(e.first_name), log2vis(e.last_name), Paragraph(get_phones(e), styleRow9), 
                 log2vis(e.mail), Paragraph(log2vis(e.address), styleRow9), log2vis(e.work_start.strftime('%d/%m/%Y')),
                 log2vis(unicode(e.employment_terms and e.employment_terms.hire_type or '---')),
                 Paragraph(get_account_str(e), styleRow9),
                 Paragraph('<br/>'.join([log2vis(p.name) for p in e.projects.all()]), styleRow9)]

            row.reverse()
            rows.append(row)

        data = [headers]
        data.extend(rows)
        t = Table(data, colWidths, style = saleTableStyle, repeatRows = 1)
        flows.append(t)
        flows.extend([PageBreak()])
        
        flows.extend([Paragraph(log2vis(u'נייס האוס - %s עובדים' % len(self.nhemployees)), styleSubTitleBold),
                      Spacer(0,10)])
        
        headers = [log2vis(name) for name in [u'מס"ד',u'פרטי\nשם',u'משפחה\nשם',u'טלפון',u'דוא"ל',u'כתובת',u'העסקה\nתחילת',u'העסקה\nסוג',u'חשבון\nפרטי']]
        colWidths = [None,None,None,110,90,70,None,30,60]
        
        colWidths.reverse()
        headers.reverse()
        
        rows = []
        
        nhbranch = None
        for e in self.nhemployees:
            if nhbranch in e.current_nhbranches:
                row = [log2vis(unicode(e.nhbranch)), None,None,None,None]
                row.reverse()
                rows.append(row)
                nhbranch = e.nhbranch

            row=[e.id, log2vis(e.first_name), log2vis(e.last_name), Paragraph(get_phones(e), styleRow9),
                 log2vis(e.mail), Paragraph(log2vis(e.address), styleRow9), log2vis(e.work_start.strftime('%d/%m/%Y')),
                 log2vis(unicode(e.employment_terms and e.employment_terms.hire_type or '')),
                 Paragraph(get_account_str(e), styleRow9)]
            row.reverse()
            rows.append(row)
                
        data = [headers]
        data.extend(rows)
        t = Table(data, colWidths, style = saleTableStyle, repeatRows = 1)
        flows.append(t)
               
        return flows
    
    def get_story(self):
        story = [Spacer(0,40)]
        story.append(titlePara(u'מצבת עובדים'))
        story.append(Spacer(0, 10))
        story.extend(self.employeeFlows())
        return story

class MonthDemandWriter(DocumentBase):

    def __init__(self, demand, to_mail=False):
        super(MonthDemandWriter, self).__init__()
        self.demand = demand
        self.signup_adds = self.demand.project.commissions.commission_by_signups
        self.to_mail = to_mail
    def toPara(self):
        contact = self.demand.project.demand_contact
        s = log2vis(u'בס"ד') + '<br/><br/>'
        s += '<u>%s</u><br/>' % log2vis(u'לכבוד')
        s += '<b>' + log2vis(u'חברת %s' % contact.company) + '<br/>'
        s += log2vis(u'לידי %s' % unicode(contact)) + '<br/>'
        s += log2vis(u'תפקיד : %s</b>' % contact.role) + '<br/></b>'
        s += log2vis(u'א.ג.נ')
        return Paragraph(s, styleN)
    def addFirst(self, canv, doc):
        super(MonthDemandWriter, self).addFirst(canv, doc)
        frame1 = Frame(300, 580, 250, 200)
        frame1.addFromList([self.toPara()], canv)
    def introPara(self):
        project_commissions = self.demand.project.commissions
        if project_commissions.include_lawyer == None:
            lawyer_str = u''
        elif project_commissions.include_lawyer == False:
            lawyer_str = u', לא כולל שכ"ט עו"ד'
        else:
            lawyer_str = u', כולל שכ"ט עו"ד'
        tax_str = project_commissions.include_tax and u'כולל מע"מ' or u'לא כולל מע"מ'
        s = log2vis(u'א. רצ"ב פירוט דרישתנו לתשלום בגין %i עסקאות שנחתמו החודש.' %
                    self.demand.get_sales().count()) + '<br/>'
        s += log2vis(u'ב. סה"כ מכירות (%s%s) - %s ש"ח.' %
                     (tax_str, lawyer_str, commaise(self.demand.get_sales().total_price_final()))) + '<br/>'
        s += log2vis(u'ג. עמלתנו (כולל מע"מ) - %s ש"ח (ראה פירוט רצ"ב).' % 
                    commaise(self.demand.get_total_amount())) + '<br/>'
        s += log2vis(u'ד. נא בדיקתכם ואישורכם לתשלום לתאריך %s אודה.' % datetime.now().strftime('31/%m/%Y')) + '<br/>'
        s += log2vis(u'ה. במידה ויש שינוי במחירי הדירות ו\או שינוי אחר') + '<br/>'
        s += log2vis(u'אנא עדכנו אותנו בפקס ו\או בטלפון הרצ"ב על גבי דרישה זו.   ') + '<br/>'
        s += log2vis(u'ו. לנוחיותכם, הדרישה מועברת אליכם גם במייל וגם בפקס.')
        return Paragraph(s, ParagraphStyle(name='into', fontName='David', fontSize=14,
                                           alignment=TA_RIGHT, leading=16))
    def zilberBonusFlows(self):
        logger = logging.getLogger('pdf')
        logger.info('starting zilberBonusFlows')
        
        flows = [tableCaption(caption=log2vis(u'נספח ב - דו"ח חסכון בהנחה')), Spacer(0,20),
                 tableCaption(caption=log2vis(u'מדד בסיס - %s' % self.demand.project.commissions.c_zilber.base_madad)),
                 Spacer(0,30)]
        
        headers = [log2vis(n) for n in [u'מס"ד',u'דרישה\nחודש', u'שם הרוכשים', u'ודירה\nבניין', u'חוזה\nתאריך', u'עמלה\nלחישוב\nמחיר', u'0 דו"ח\nמחירון', 
                                        u'חדש\nמדד', u'60%\nממודד\nמחירון', u'מחיר\nהפרש', u'בהנחה\nחסכון\nשווי']]
        
        colWidths  =[None,None,100,None,None,None,40,40,40,40,40]
        colWidths.reverse()
        headers.reverse()
        rows = []
        i = 1
        total_prices, total_adds, total_doh0price, total_memudad, total_diff = 0, 0, 0, 0, 0
        demand = self.demand
        base_madad = demand.project.commissions.c_zilber.base_madad
                
        logger.debug(str({'base_madad':base_madad}))
        
        while demand != None:
            logger.info('starting to write bonuses for %(demand)s', {'demand':demand})

            sales = demand.get_sales().select_related('house__building')
            
            current_madad = max((demand.get_madad(), base_madad))
            
            logger.debug(str({'sales':sales, 'current_madad':current_madad}))
            
            for s in sales:
                logger.info('starting to write bonus for sale #%(id)s', {'id':s.id})
                
                i += 1
                actual_demand = s.actual_demand
                if actual_demand:
                    row = ['%s-%s' % (actual_demand.id, i),'%s/%s' % (actual_demand.month, actual_demand.year)]
                else:
                    row = [None, None]
                    
                commission_details = dict(s.project_commission_details.values_list('commission','value'))
                
                doh0price = commission_details.get('latest_doh0price', 0)
                memudad = commission_details.get('memudad', 0)
                price_memduad_diff = s.price_final - memudad
                
                row.extend([log2vis(s.clients), '%s/%s' % (unicode(s.house.building), unicode(s.house)), 
                            s.sale_date.strftime('%d/%m/%y'), commaise(s.price_final), commaise(doh0price), 
                            current_madad, commaise(memudad), commaise(price_memduad_diff), commaise(s.zdb)])

                row.reverse()
                rows.append(row)
                
                total_prices += s.price
                total_adds += s.zdb
                total_doh0price += doh0price
                total_memudad += memudad
                total_diff += price_memduad_diff
 
            if demand.zilber_cycle_index() == 1:
                break
            
            demand = demand.get_previous_demand()
            
        sum_row = [Paragraph(log2vis(u'סה"כ'), styleSaleSumRow), None, None, None, None, 
                   Paragraph(commaise(total_prices), styleSaleSumRow), 
                   Paragraph(commaise(total_doh0price), styleSaleSumRow),
                   None,
                   Paragraph(commaise(total_memudad), styleSaleSumRow), 
                   Paragraph(commaise(total_diff), styleSaleSumRow), 
                   Paragraph(commaise(round(total_adds)), styleSaleSumRow)]
        
        sum_row.reverse()
        rows.append(sum_row)
        data = [headers]
        data.extend(rows)
        t = Table(data, colWidths, style = saleTableStyle, repeatRows = 1)
        flows.append(t)
        return flows
    
    def zilberAddsFlows(self):
        logger = logging.getLogger('pdf')
        logger.info('starting zilberAddsFlows')
        
        flows = [tableCaption(caption=log2vis(u'נספח א - הפרשי קצב מכירות לדרישה')),
                 Spacer(0,30)]
        headers = [log2vis(n) for n in [u'דרישה\nחודש', u'שם הרוכשים', u'ודירה\nבניין',u'מכירה\nתאריך', u'חוזה\nמחיר', u'עמלה\nלחישוב\nמחיר',
                                        u'בדרישה\nעמלה',u'חדשה\nעמלה', u'הפרש\nאחוז', u'בש"ח\nהפרש']]
        colWidths = [None,80,None,None,None,None,None,None,None,None]
        colWidths.reverse()
        headers.reverse()
        rows = []
        demand = self.demand
        sales = list(demand.get_sales().select_related('house__building'))
        total_prices, total_prices_finals, total_adds = 0, 0, 0
        
        while demand.zilber_cycle_index() > 1:
            demand = demand.get_previous_demand()
            # adds sales of the current demand before the sales we already have because we are iterating in reverse
            demand_sales = list(demand.get_sales().select_related('house__building'))
            demand_sales.extend(sales)
            sales = demand_sales
        
        for s in sales:
            try:
                sale_add = s.project_commission_details.get(commission='c_zilber_add').value
                sale_base_with_add = s.project_commission_details.get(commission='c_zilber_base_with_add').value
            except ObjectDoesNotExist:
                continue
                                    
            row = [log2vis('%s/%s' % (s.actual_demand.month, s.actual_demand.year)), clientsPara(s.clients), 
                   '%s/%s' % (unicode(s.house.building), unicode(s.house)), s.sale_date.strftime('%d/%m/%y'), 
                   commaise(s.price), commaise(s.price_final), s.pc_base, sale_base_with_add, sale_base_with_add - s.pc_base, commaise(sale_add)]

            row.reverse()
            rows.append(row)
            total_prices += s.price
            total_prices_finals += s.price_final
            total_adds += round(sale_add)
             
        sum_row = [Paragraph(log2vis(u'סה"כ'), styleSaleSumRow), None, None, None, Paragraph(commaise(total_prices), styleSaleSumRow),
                   Paragraph(commaise(total_prices_finals), styleSaleSumRow), None, None, None, 
                   Paragraph(commaise(total_adds), styleSaleSumRow)]
        sum_row.reverse()
        rows.append(sum_row)
        data = [headers]
        data.extend(rows)
        t = Table(data, colWidths, style = saleTableStyle, repeatRows = 1)
        flows.append(t)
        return flows
                        
    def signupFlows(self):
        flows = [tableCaption(caption=log2vis(u'להלן תוספות להרשמות מחודשים קודמים')),
                 Spacer(0,30)]
        headers = [log2vis(n) for n in [u'הרשמה\nתאריך',u'דרישה\nחודש', u'הרוכשים\nשם', u'ודירה\nבניין', 
                                        u'חוזה\nתאריך',u'חוזה\nמחיר', u'ששולמה\nעמלה', 
                                        u'חדשה\nעמלה', u'עמלה\nהפרש', u'בש"ח\nהפרש']]
        headers.reverse()
        colWidths = [None,None,80,None,None,None,35,30,30,None]
        colWidths.reverse()
        rows = []
        total = 0

        for subSales in self.demand.get_affected_sales().values():
            for s in subSales.all():
                singup = s.house.get_signup() 
                row = [singup.date.strftime('%d/%m/%y'), '%s/%s' % (s.contractor_pay_month, s.contractor_pay_year), 
                       clientsPara(s.clients), '%s/%s' % (unicode(s.house.building), unicode(s.house)), 
                       s.sale_date.strftime('%d/%m/%y'), commaise(s.price)]
                s.restore_date = self.demand.get_previous_demand().finish_date
                c_final_old = s.c_final
                s.restore_date = self.demand.finish_date
                c_final_new = s.c_final
                diff = c_final_new - c_final_old
                total += int(diff * s.price_final / 100)
                row.extend([c_final_old, c_final_new, diff, commaise(diff * s.price_final / 100)])
                row.reverse()
                rows.append(row)

        sum_row = [Paragraph(log2vis(u'סה"כ'), styleSaleSumRow),None,None,None,None,None,None,None,None,Paragraph(commaise(total), styleSaleSumRow)]
        sum_row.reverse()
        rows.append(sum_row)      
        data = [headers]
        data.extend(rows)
        t = Table(data, colWidths, style = saleTableStyle, repeatRows = 1)
        flows.append(t)
        return flows
    def signup_counts_para(self):
        s = log2vis(u'סה"כ הרשמות מצטבר לחישוב עמלה') + '<br/>'
        s += log2vis(u', '.join(u'%s מ - %s/%s' % (count, month[0], month[1]) 
                                for month, count in self.demand.get_signup_months().items())) + '<br/>'
        count = 0
        for subSales in self.demand.get_affected_sales().values():
            count += subSales.count()
        s += log2vis(u' + %s מחודשים קודמים' % count)
        return Paragraph(s, ParagraphStyle('signup_months', fontName='David', fontSize=10, alignment=TA_CENTER))
    def saleFlows(self):
        sales = self.demand.get_sales()
        names = [u'מס"ד']
        colWidths = [35]
        contract_num, discount, final = False, False, False
        zilber = self.demand.project.is_zilber()
        
        if sales[0].contract_num:
            names.append(u"חוזה\nמס'")
            colWidths.append(40)
            contract_num = True
        if self.signup_adds:
            names.append(u'הרשמה\nתאריך')
            colWidths.append(None)
        names.extend([u'שם הרוכשים',u'ודירה\nבניין',u'מכירה\nתאריך', u'חוזה\nמחיר'])
        colWidths.extend([65, None,None,45])
        
        if zilber:
            names.extend([u'רישום\nהוצאות',u'מזומן\nהנחת', u'מפרט\nהוצאות',u'עו"ד\nשכ"ט', u'נוספות\nהוצאות'])
            colWidths.extend([30,30,30,None,30])

        if not self.demand.project.id == 5:
            if sales[0].discount or sales[0].allowed_discount:
                names.extend([u'ניתן\nהנחה\n%',u'מותר\nהנחה\n%'])
                colWidths.extend([None,None])
                discount = True
                
        names.extend([u'עמלה\nלחישוב\nמחיר', u'בסיס\nעמלת\n%',u'בסיס\nעמלת\nשווי'])
        colWidths.extend([45,None,None])
        if self.demand.project.commissions.b_discount_save_precentage:
            names.extend([u'חסכון\nבונוס\n%',u'חסכון\nבונוס\nשווי', u'סופי\nעמלה\n%',u'סופי\nעמלה\nשווי'])
            colWidths.extend([30,30,None,None])
            final = True
        colWidths.reverse()
        names.reverse()
        headers = [log2vis(name) for name in names]
        i=1
        flows = [tableCaption(), Spacer(0,10)]
        if self.signup_adds:
            flows.extend([self.signup_counts_para(), Spacer(0,10)])
        rows = []
        total_lawyer_pay, total_pc_base_worth, total_pb_dsp_worth = 0, 0 ,0
        
        commissions = self.demand.project.commissions
        
        for s in sales:
            s.restore = True
            row = ['%s-%s' % (self.demand.id, i)]
            if contract_num:
                row.append(s.contract_num)
            if self.signup_adds:
                signup = s.house.get_signup()
                row.append(signup and signup.date.strftime('%d/%m/%y') or '')
            row.extend([clientsPara(s.clients), '%s/%s' % (unicode(s.house.building), unicode(s.house)), 
                        s.sale_date.strftime('%d/%m/%y'), commaise(s.price)])
            if zilber:
                if s.include_registration:
                    row.append(None)
                else:
                    row.append(commaise(commissions.registration_amount))
                lawyer_pay = s.price_include_lawyer and (s.price - s.price_no_lawyer) or s.price * 0.015
                total_lawyer_pay += lawyer_pay
                row.extend([None,commaise(s.specification_expense),commaise(lawyer_pay),commaise(s.other_expense)])

            if discount:
                row.extend([s.discount, s.allowed_discount])
                
            row.extend([commaise(s.price_final),s.pc_base, commaise(s.pc_base_worth)])
            total_pc_base_worth += s.pc_base_worth
            
            if final:
                row.extend([s.pb_dsp, commaise(s.pb_dsp_worth), s.c_final, commaise(s.c_final_worth)])
                total_pb_dsp_worth += s.pb_dsp_worth
                
            row.reverse()#reportlab prints columns ltr
            rows.append(row)
            i+=1

        row = [Paragraph(log2vis(u'סה"כ'), styleSaleSumRow)]
        if contract_num:
            row.append(None)
        if self.signup_adds:
            row.append(None)
        row.extend([None,Paragraph(log2vis('%s' % self.demand.get_sales().count()), styleSaleSumRow),None])
        row.append(Paragraph(commaise(self.demand.get_sales().total_price()), styleSaleSumRow))
        if zilber:
            row.extend([None,None,None,Paragraph(commaise(total_lawyer_pay), styleSaleSumRow),None])
        if discount:
            row.extend([None,None])
        if final:
            row.extend([None,Paragraph(commaise(total_pc_base_worth), styleSaleSumRow),
                        None,Paragraph(commaise(total_pb_dsp_worth), styleSaleSumRow),
                        None,Paragraph(commaise(self.demand.sales_commission), styleSaleSumRow)])
        else:
            row.extend([Paragraph(commaise(self.demand.get_sales().total_price_final()), styleSaleSumRow),
                        None,Paragraph(commaise(self.demand.sales_commission), styleSaleSumRow)])
        row.reverse()
        rows.append(row)
        data = [headers]
        data.extend(rows)
        t = Table(data, colWidths, style = saleTableStyle, repeatRows = 1)
        flows.append(t)
        
        return flows
    def remarkPara(self):
        s = '<b><u>%s</u></b><br/>' % log2vis(u'הערות לדרישה')
        remarks = self.demand.remarks
        if remarks != None and len(remarks.lstrip().rstrip())>0:
            s += log2vis(remarks.lstrip().rstrip())
        else:
            s += log2vis(u'אין')
        return Paragraph(s, ParagraphStyle(name='remarkPara', fontName='David', fontSize=13, 
                                           leading=16, alignment=TA_RIGHT))
    def addsPara(self):
        s = '<br/>'.join([log2vis(u'%s - %s ש"ח' % (d.reason, commaise(d.amount))) for d in self.demand.diffs.all()]) + '<br/>'
        s += '<b>%s</b>' % log2vis(u'סה"כ : %s ש"ח' % commaise(self.demand.get_total_amount())) + '<br/>'
        return Paragraph(s, ParagraphStyle(name='addsPara', fontName='David', fontSize=14, 
                                           leading=16, alignment=TA_LEFT))
    def get_story(self):
        story = [Spacer(0,100)]
        title = u'הנדון : עמלה לפרויקט %s לחודש %s/%s' % (self.demand.project, 
                                                          self.demand.month, 
                                                          self.demand.year)
        story.append(titlePara(title))
        story.append(Spacer(0, 10))
        subTitle = u"דרישה מס' %s" % self.demand.id
        if self.demand.project.is_zilber():
            subTitle += u' (%s מתוך %s)' % (self.demand.zilber_cycle_index(), models.CZilber.Cycle)

        story.append(Paragraph('<u>%s</u>' % log2vis(subTitle), styleSubTitleBold))
        story.extend([Spacer(0,20), self.introPara(), Spacer(0,20)])
        story.extend(self.saleFlows())
        if self.demand.diffs.count() > 0:
            story.extend([Spacer(0, 20), self.addsPara()])
        if self.demand.project.is_zilber() and (self.demand.include_zilber_bonus() or not self.to_mail):
            story.extend([PageBreak(), Spacer(0,30)])
            story.extend(self.zilberAddsFlows())
            story.extend([PageBreak(), Spacer(0,30)])
            story.extend(self.zilberBonusFlows())
        story.extend([Spacer(0, 20), self.remarkPara(), sigPara()]) 
        if self.signup_adds:
            story.extend([PageBreak(), Spacer(0,30), titlePara(u'נספח א')])
            story.extend(self.signupFlows())
        return story

class MultipleDemandWriter:
    def __init__(self, demands, title, show_project, show_month):
        self.demands = demands
        self.title = title
        self.show_month = show_month
        self.show_project = show_project
    @property
    def pages_count(self):
        return len(self.demands) % 20 + 1
    def addTemplate(self, canv, doc):
        frame2 = Frame(0, 680, 650, 150)
        frame2.addFromList([nhLogo(), datePara()], canv)
        frame3 = Frame(50, 20, 150, 40)
        frame3.addFromList([Paragraph(log2vis(u'עמוד %s מתוך %s' % (self.current_page, self.pages_count)), 
                            ParagraphStyle('pages', fontName='David', fontSize=13,))], canv)
        frame4 = Frame(50, 30, 500, 70)
        frame4.addFromList([nhAddr()], canv)
        self.current_page += 1
    def projectsFlows(self):
        flows, headers, colWidths = [], [], []
        if self.show_project:
            headers.extend([log2vis(n) for n in [u'שם היזם', u'שם הפרוייקט']])
            colWidths.extend([90,140])
            sumRow = [None, None]
        if self.show_month:
            headers.append(log2vis(u'חודש'))
            colWidths.append(None)
            sumRow = [None]
        headers.extend(log2vis(n) for n in[u'סה"כ מכירות', u'סה"כ עמלה', u'מס ח-ן', u'סך ח-ן', u'מס צק', u'סך צק'])
        headers.reverse()
        colWidths.extend([60,60,50,50,50,50])
        colWidths.reverse()
        rows = []
        rowHeights = [28]
        index, total_sales_amount, total_amount = 0,0,0
        for d in self.demands:
            row = []
            if self.show_project:
                project_name = d.project.name.count(d.project.city) > 0 and log2vis(d.project.name) or log2vis(u'%s %s' % (d.project.name, d.project.city))
                row.extend([log2vis(d.project.initiator), project_name])
            if self.show_month:
                row.append('%s/%s' % (d.month, d.year))
            row.extend([commaise(d.get_sales().total_price()), commaise(d.get_total_amount())])
            row.extend([Paragraph('<br/>'.join([str(i.num) for i in d.invoices.all()]), styleRow9),
                        Paragraph('<br/>'.join([commaise(i.amount) for i in d.invoices.all()]), styleRow9),
                        Paragraph('<br/>'.join([str(p.num) for p in d.payments.all()]), styleRow9),
                        Paragraph('<br/>'.join([commaise(p.amount) for p in d.payments.all()]), styleRow9)])
            row.reverse()
            rows.append(row)
            maxSubRows = max([1, d.invoices.count(), d.payments.count()])
            rowHeights.append(18 * maxSubRows)
            index += 1
            total_sales_amount += d.get_sales().total_price()
            total_amount += d.get_total_amount()
            
            if index % 20 == 0:
                data = [headers]
                data.extend(rows)
                table = Table(data, colWidths, rowHeights)
                table.setStyle(projectTableStyle)
                flows.extend([table, PageBreak(), Spacer(0,50)])
                rows = []
                rowHeights = [28]
                
        sumRow.extend([Paragraph(commaise(total_sales_amount), styleSumRow), 
                       Paragraph(commaise(total_amount), styleSumRow), None, None, None, None])
        sumRow.reverse()
        rows.append(sumRow)
        rowHeights.append(28)
        data = [headers]
        data.extend(rows)
        table = Table(data, colWidths, rowHeights)
        table.setStyle(projectTableStyle)
        flows.append(table)
        return flows
    
    def build(self, filename):
        self.current_page = 1
        doc = SimpleDocTemplate(filename)
        story = [Spacer(0,50)]
        story.append(titlePara(self.title))
        story.append(Spacer(0, 10))
        story.extend(self.projectsFlows())
        doc.build(story, self.addTemplate, self.addTemplate)
        return doc.canv

class EmployeeSalariesBookKeepingWriter:
    def __init__(self, salaries, title, nhsales = None):
        self.salaries, self.title, self.nhsales = salaries, title, nhsales
    @property
    def pages_count(self):
        pages = len(self.salaries) / 28 + 1
        if self.nhsales:
            pages += len(self.nhsales) / 28 + 1
        return pages
    def addTemplate(self, canv, doc):
        frame2 = Frame(0, 680, 650, 150)
        frame2.addFromList([nhLogo(), datePara()], canv)
        frame3 = Frame(50, 20, 150, 40)
        frame3.addFromList([Paragraph(log2vis(u'עמוד %s מתוך %s' % (self.current_page, self.pages_count)), 
                            ParagraphStyle('pages', fontName='David', fontSize=13,))], canv)
        frame4 = Frame(50, 30, 500, 70)
        frame4.addFromList([nhAddr()], canv)
        self.current_page += 1
    def nhsalesFlows(self):
        flows = []
        headers = [log2vis(n) for n in [u'מס"ד',u'הרוכשים\nשם',u'התשלום\nסכום',u"תיווך\nשרותי\nהזמנת\nמס'",u'חשבונית',
                                        u"זמנית\nקבלה\nמס'",u'תשלום\nסוג',u"מס' צ'ק",u'בנק',u'מטפל\nסוכן',
                                        u'תשלום\nתאריך',u"סניף\nמס'",u'הערות']]
        headers.reverse()
        colWidths = [None, 70, None, None, 40, None, None, 40, None, 70, None, None, 20]
        colWidths.reverse()
        rows = []
        remarks_str = ''
        i = 0
        for s in self.nhsales:
            for side in s.nhsaleside_set.all():
                clients = log2vis(side.name1) + '<br/>' + log2vis(side.name2 or '')
                invoice = side.invoices.count() > 0 and side.invoices.all()[0]
                if invoice:
                    invoice_str = '%s<br/>%s' % (invoice.date.strftime('%d/%m/%y'), invoice.num and str(invoice.num) or '')
                else:
                    invoice_str = ''
                invoice_para = Paragraph(invoice_str, styleRow9)
                payments = side.payments.all()
                row = [s.num, Paragraph(clients, styleRow9), commaise(side.net_income), side.voucher_num, 
                       invoice_para, side.temp_receipt_num, 
                       Paragraph('<br/>'.join([log2vis(unicode(p.payment_type)) for p in payments]), styleRow9),
                       Paragraph('<br/>'.join([unicode(p.num) for p in payments]), styleRow9),
                       Paragraph('<br/>'.join([log2vis(p.bank) for p in payments]), styleRow9),
                       log2vis(unicode(side.signing_advisor)),
                       Paragraph('<br/>'.join([p.payment_date.strftime('%d/%m/%y') for p in payments]), styleRow9),
                       Paragraph('<br/>'.join([unicode(p.branch_num) for p in payments]), styleRow9),
                       side.remarks and '*']
                row.reverse()
                rows.append(row)
                if side.remarks:
                    remarks_str += log2vis(side.name1 + ' ' + (side.name2 or '') + ' - ' + side.remarks) + '<br/>'
            i += 1
            if i % 27 == 0 or i == len(self.nhsales):
                data = [headers]
                data.extend(rows)
                t = Table(data, colWidths)
                t.setStyle(nhsalariesTableStyle)
                flows.append(t)
                if i < len(self.nhsales):
                    flows.extend([PageBreak(), Spacer(0, 50)])
                rows = []
        flows.append(Spacer(0,10))
        flows.append(Paragraph(remarks_str, styleNormal13))
        flows.append(Spacer(0,10))
        flows.append(Paragraph(log2vis(u'לתשומת לבך'), styleSubTitleBold))
        flows.append(Spacer(0,10))
        flows.append(Paragraph(log2vis(u"יש להוציא את השכר לעובדים לאחר בדיקה שכל הצ'קים התקבלו והחשבוניות הוצאו."), styleNormal13))
        flows.append(Paragraph(log2vis(u"במידה ויש צ'קים דחויים\או שלא הגיעו נא לעדכן את אלי."), styleNormal13))
        return flows
    def salariesFlows(self):
        flows = []
        headers = [log2vis(n) for n in [u'מס"ד',u'העובד\nשם',u'העסקה\nסוג',u'לתשלום\nשווי צק',u'הוצאות\nהחזר',
                                        u'ברוטו\nשווי',u'חשבונית\nשווי',u'ניכוי מס\nשווי',u'הלוואה\nהחזר',u'תלוש נטו\nשווי',
                                        u'הערות']]
        groups = [log2vis(u'לשימוש הנה"ח בלבד'), None, None, None, None, None, log2vis(u'תשלום צקים לעובד')]
        headers.reverse()
        colWidths = [None for i in headers]
        colWidths.reverse()
        rows = []
        remarks_str = ''
        i = 0
        for es in self.salaries:
            employee = es.get_employee()
            terms = employee.employment_terms
            hire_type = terms and unicode(terms.hire_type) or ''
            if terms and not terms.salary_net and terms.hire_type.id == models.HireType.Salaried:
                hire_type += u' - ברוטו'
            check_amount = terms.salary_net == False and log2vis(u'הנהלת חשבונות') or commaise(es.check_amount)
            row = [es.id, log2vis(unicode(employee)), log2vis(hire_type), check_amount, commaise(es.refund),
                   commaise(es.bruto),commaise(es.invoice_amount),None,commaise(es.loan_pay), commaise(es.neto), es.pdf_remarks and '*' or '']
            row.reverse()
            rows.append(row)
            
            if es.pdf_remarks:
                remarks_str += '<u><b>' + log2vis(unicode(employee) + '</b></u>' + ' ' + (es.pdf_remarks)) + '<br/>'
            
            i += 1
            if i % 27 == 0 or i == len(self.salaries):
                data = [groups, headers]
                data.extend(rows)
                t = Table(data, colWidths)
                t.setStyle(salariesTableStyle)
                flows.append(t)
                if i < len(self.salaries):
                    flows.extend([PageBreak(), Spacer(0, 50)])
                rows = []
                
        if remarks_str:
            flows.append(Spacer(0,10))
            flows.append(Paragraph(remarks_str, styleNormal13))
        
        return flows
    def build(self, filename):
        self.current_page = 1
        doc = SimpleDocTemplate(filename)
        story = [Spacer(0,50)]
        story.append(titlePara(self.title))
        story.append(Spacer(0, 10))
        story.extend(self.salariesFlows())
        if self.nhsales:
            story.extend([PageBreak(),titlePara(u"אישור צ'קים וחשבוניות"),Spacer(0,20)])
            story.extend(self.nhsalesFlows())
        doc.build(story, self.addTemplate, self.addTemplate)
        return doc.canv

class EmployeeSalariesWriter:
    def __init__(self, salaries, title, show_employee, show_month):
        self.salaries, self.title, self.show_employee, self.show_month = salaries, title, show_employee, show_month
    @property
    def pages_count(self):
        return len(self.salaries) / 28 + 1
    def addTemplate(self, canv, doc):
        frame2 = Frame(0, 680, 650, 150)
        frame2.addFromList([nhLogo(), datePara()], canv)
        frame3 = Frame(50, 20, 150, 40)
        frame3.addFromList([Paragraph(log2vis(u'עמוד %s מתוך %s' % (self.current_page, self.pages_count)), 
                            ParagraphStyle('pages', fontName='David', fontSize=13,))], canv)
        frame4 = Frame(50, 30, 500, 70)
        frame4.addFromList([nhAddr()], canv)
        self.current_page += 1
    def salariesFlows(self):
        flows = []
        headers = []
        if self.show_employee:
            headers.append(log2vis(u'העובד\nשם'))
        if self.show_month:
            headers.append(log2vis(u'חודש'))
        headers.append(log2vis(u'העסקה\nסוג'))
        headers.append(log2vis(u'הצק\nסכום'))
        headers.reverse()
        colWidths = [None,None,None,None,None,None,None,None]
        colWidths.reverse()
        rows = []
        i = 0
        for es in self.salaries:
            terms = es.employee.employment_terms
            row = []
            if self.show_employee:
                row.append(log2vis(unicode(es.employee)))
            if self.show_month:
                row.append('%s/%s' % (es.month, es.year))
            row.extend([log2vis(u'%s - %s' % (terms.hire_type.name, terms.salary_net and u'נטו' or u'ברוטו'))])
            row.append(commaise(es.check_amount))
            row.reverse()
            rows.append(row)
            i += 1
            if i % 27 == 0 or i == len(self.salaries):
                data = [headers]
                data.extend(rows)
                t = Table(data, colWidths)
                t.setStyle(saleTableStyle)
                flows.append(t)
                if i < len(self.salaries):
                    flows.extend([PageBreak(), Spacer(0, 50)])
                rows = []

        return flows
    def build(self, filename):
        self.current_page = 1
        doc = SimpleDocTemplate(filename)
        story = [Spacer(0,50)]
        story.append(titlePara(self.title))
        story.append(Spacer(0, 10))
        story.extend(self.salariesFlows())
        doc.build(story, self.addTemplate, self.addTemplate)
        return doc.canv
    
class SalariesBankWriter:
    def __init__(self, salaries, month, year):
        self.salaries = salaries
        self.title = u'שכר להעברה בנקאית לחודש %s/%s' % (month, year)
    @property
    def pages_count(self):
        return len(self.salaries) / 28 + 1
    def addTemplate(self, canv, doc):
        frame2 = Frame(0, 680, 650, 150)
        frame2.addFromList([nhLogo(), datePara()], canv)
        frame3 = Frame(50, 20, 150, 40)
        frame3.addFromList([Paragraph(log2vis(u'עמוד %s מתוך %s' % (self.current_page, self.pages_count)), 
                            ParagraphStyle('pages', fontName='David', fontSize=13,))], canv)
        frame4 = Frame(50, 30, 500, 70)
        frame4.addFromList([nhAddr()], canv)
        self.current_page += 1
    def salariesFlows(self):
        logger = logging.getLogger('pdf')
        logger.info('starting to write %(salary_count)s salaries for bank', {'salary_count':len(self.salaries)})
        
        flows = []
        headers = [log2vis(n) for n in [u'העובד\nמס', u'פרטי\nשם', u'משפחה\nשם', u'ת.ז', u'המוטב\nשם', u'להעברה\nסכום', u'חשבון\nמספר', u'בנק',
                                        u'סניף\nכתובת', u'סניף\nמספר', u'הערות']]
        colWidths = [None for header in headers]
        headers.reverse()
        colWidths.reverse()
        rows = []
        i = 0
        for salary in self.salaries:
            i+=1
            employee = salary.get_employee()
            if salary.neto:
                account = employee.account
                if not account:
                    account = models.Account()
                    
                row = [employee.id, log2vis(employee.first_name), log2vis(employee.last_name), employee.pid, log2vis(employee.payee),
                       commaise(salary.neto), account.num, log2vis(account.bank), log2vis(account.branch), account.branch_num, '']
                
                row.reverse()
                rows.append(row)
            else:
                logger.warn('skipping salary for employee #%(employee_id)s - %(employee_name)s because he does not have neto salary',
                            {'employee_id':employee.id, 'employee_name':employee})
                
            if len(rows) % 27 == 0 or i == len(self.salaries):
                data = [headers]
                data.extend(rows)
                t = Table(data, colWidths)
                t.setStyle(saleTableStyle)
                flows.append(t)
                if i < len(self.salaries):
                    flows.extend([PageBreak(), Spacer(0, 50)])
                rows = []

        logger.info('finished writing salaries for bank')

        return flows
    def build(self, filename):
        self.current_page = 1
        doc = SimpleDocTemplate(filename)
        story = [Spacer(0,50)]
        story.append(titlePara(self.title))
        story.append(Spacer(0, 10))
        story.extend(self.salariesFlows())
        doc.build(story, self.addTemplate, self.addTemplate)
        return doc.canv

class PricelistWriter:
    def __init__(self, pricelist, houses, title, subtitle):
        self.pricelist, self.houses, self.title, self.subtitle = pricelist, houses, title, subtitle
    @property
    def pages_count(self):
        return len(self.houses) / 28 + 2
    def addTemplate(self, canv, doc):
        frame3 = Frame(50, 20, 150, 40)
        frame3.addFromList([Paragraph(log2vis(u'עמוד %s מתוך %s' % (self.current_page, self.pages_count)), 
                            ParagraphStyle('pages', fontName='David', fontSize=13,))], canv)
        frame4 = Frame(50, 670, 500, 70)
        frame4.addFromList([titlePara(self.title), Paragraph(log2vis(self.subtitle), styleSubTitle)], canv)
        self.current_page += 1
    def housesFlows(self):
        flows = []
        headers = [log2vis(n) for n in [u'מס', u'קומה', u'דירה\nסוג', u'חדרים\nמס', u'נטו\nשטח', u'גינה\nמרפסת/\nשטח', u'מחיר',
                                        u'חניה', u'מחסן', u'הערות']]
        headers.reverse()
        colWidths = [None,None,70,None,None,None,None,None,None,None]
        colWidths.reverse()
        rows = []
        i = 0
        for h in self.houses:
            parkings = '<br/>'.join([log2vis(unicode(p.num)) for p in h.parkings.all()])
            storages = '<br/>'.join([log2vis(unicode(s.num)) for s in h.storages.all()])
            row = [h.num, h.floor,  log2vis(unicode(h.type)), h.rooms, h.net_size, h.garden_size, 
                   h.price and commaise(h.price) or '-', Paragraph(parkings, styleRow), Paragraph(storages, styleRow), 
                   log2vis(h.remarks[:15] + (len(h.remarks)>15 and ' ...' or ''))]
            row.reverse()
            rows.append(row)
            i += 1
            if i % 27 == 0:
                data = [headers]
                data.extend(rows)
                t = Table(data, colWidths)
                t.setStyle(saleTableStyle)
                flows.append(t)
                if i < len(self.houses):
                    flows.extend([PageBreak(), Spacer(0, 80)])
                rows = []
        row = [None, None, None, None, None, None, None, None, 
               Paragraph(log2vis(u'סה"כ'), styleSumRow), Paragraph(str(len(self.houses)), styleSumRow)]
        row.reverse()
        rows.append(row)
        data = [headers]
        data.extend(rows)
        t = Table(data, colWidths)
        t.setStyle(saleTableStyle)
        flows.append(t)
        return flows
    def build(self, filename):
        self.current_page = 1
        doc = SimpleDocTemplate(filename)
        story = [Spacer(0,80)]
        story.extend(self.housesFlows())
        story.extend([PageBreak(), Spacer(0,80)])
        settle_date = self.pricelist.settle_date
        story.append(Paragraph(log2vis(u'מועד אכלוס : ' + (settle_date and settle_date.strftime('%d/%m/%Y') or '----')),
                               ParagraphStyle('1', fontName='David',fontSize=14, leading=15, alignment=TA_RIGHT)))
        story.append(Paragraph(log2vis('מדד תשומות הבנייה : ' + str(models.MadadBI.objects.latest().value)),
                               ParagraphStyle('1', fontName='David',fontSize=14, leading=15, alignment=TA_LEFT)))
        include_str = log2vis(u'המחיר כולל : ' + ', '.join(ugettext(attr) for attr in ['tax','lawyer','parking','storage','registration','guarantee']
                                                           if getattr(self.pricelist, 'include_' + attr)))
        story.append(Paragraph(include_str, ParagraphStyle('1', fontName='David',fontSize=14, leading=15, alignment=TA_RIGHT)))
        include_str = log2vis(u'היתר : ' + (self.pricelist.is_permit and u'יש' or u'אין'))
        story.append(Paragraph(include_str, ParagraphStyle('1', fontName='David',fontSize=14, leading=15, alignment=TA_LEFT)))
        notinclude_str = u'המחיר אינו כולל : מס רכישה כחוק'
        if self.pricelist.include_registration == False:
            notinclude_str += ', %s  (%s)' % (ugettext('register_amount'), self.pricelist.register_amount)
        if self.pricelist.include_guarantee == False:
            notinclude_str += ', %s  (%s)' % (ugettext('guarantee_amount'), self.pricelist.guarantee_amount)
        if self.pricelist.include_lawyer == False:
            notinclude_str += ', %s  %%(%s)' % (ugettext('lawyer_fee'), self.pricelist.lawyer_fee)
        story.append(Paragraph(log2vis(notinclude_str), ParagraphStyle('1', fontName='David',fontSize=14, leading=15, alignment=TA_RIGHT)))
        story.append(Spacer(0,10))
        assets_str = '<u>%s</u><br/>' % log2vis(u'נכסים משניים פנויים')
        assets_str += log2vis(u'מחסנים : ' + ','.join(str(s.num) for s in self.pricelist.building.storages.filter(house=None))) + '<br/>'
        assets_str += log2vis(u'חניות : ' + ','.join(str(p.num) for p in self.pricelist.building.parkings.filter(house=None))) + '<br/>'
        story.append(Paragraph(assets_str, ParagraphStyle('1', fontName='David',fontSize=14, leading=15, alignment=TA_RIGHT)))
        doc.build(story, self.addTemplate, self.addTemplate)
        return doc.canv

class BuildingClientsWriter:
    def __init__(self, houses, title, subtitle):
        self.houses, self.title, self.subtitle = houses, title, subtitle
    @property
    def pages_count(self):
        return len(self.houses) / 28 + 1
    def addTemplate(self, canv, doc):
        frame3 = Frame(50, 20, 150, 40)
        frame3.addFromList([Paragraph(log2vis(u'עמוד %s מתוך %s' % (self.current_page, self.pages_count)), 
                            ParagraphStyle('pages', fontName='David', fontSize=13,))], canv)
        self.current_page += 1
    def housesFlows(self):
        flows = []
        headers = [log2vis(n) for n in [u'דירה\nמס',u'דירה\nסוג',u'נטו\nשטח',u'קומה',u'הרוכשים\nשם',u'ת.ז',u'כתובת',u'טלפונים',
                                        u'דוא"ל',u'הרשמה\nתאריך',u'חוזה\nתאריך',u'מחירון',u'חוזה\nמחיר',u'חנייה',u'מחסן',
                                        u'נלוות\nהוצאות',u'חזוי\nאכלוס\nמועד']]
        headers.reverse()
        rows = []
        total_sale_price = 0
        i = 0
        for h in self.houses:
            parkings = '<br/>'.join([log2vis(unicode(p.num)) for p in h.parkings.all()])
            storages = '<br/>'.join([log2vis(unicode(s.num)) for s in h.storages.all()])
            sale = h.get_sale()
            signup = h.get_signup()
            if sale:
                clients_name, clients_address, clients_phone = clientsPara(sale.clients), '', clientsPara(sale.clients_phone)
                sale_price = sale.price
                total_sale_price += sale.price
            else:
                clients_name, clients_address, clients_phone, sale_price = '','','',''
            row = [h.num, log2vis(unicode(h.type)), h.net_size, h.floor, clients_name, '', clients_address, clients_phone, 
                   '', signup and signup.date.strftime('%d/%m/%Y'), sale and sale.sale_date.strftime('%d/%m/%Y') or '',
                   h.price and commaise(h.price) or '-', commaise(sale_price), Paragraph(parkings, styleRow), Paragraph(storages, styleRow), 
                   '','']
            row.reverse()
            rows.append(row)
            i += 1
            if i % 27 == 0:
                data = [headers]
                data.extend(rows)
                t = Table(data)
                t.setStyle(saleTableStyle)
                flows.append(t)
                if i < len(self.houses):
                    flows.extend([PageBreak(), Spacer(0, 50)])
                rows = []
        sumRow = [Paragraph(str(self.houses.count()), styleSumRow),None,None,None,None,None,None,None,None,None,None,None, 
                  Paragraph(commaise(total_sale_price), styleSumRow), None, None, None, None]
        sumRow.reverse()
        rows.append(sumRow)
        data = [headers]
        data.extend(rows)
        t = Table(data)
        t.setStyle(saleTableStyle)
        flows.append(t)
        return flows
    def build(self, filename):
        self.current_page = 1
        doc = SimpleDocTemplate(filename, pagesize = landscape(A4))
        story = []
        story.append(titlePara(self.title))
        if self.subtitle:
            story.append(Paragraph(log2vis(self.subtitle), styleSubTitle))
        story.append(Spacer(0, 10))
        story.extend(self.housesFlows())
        doc.build(story, self.addTemplate, self.addTemplate)
        return doc.canv
