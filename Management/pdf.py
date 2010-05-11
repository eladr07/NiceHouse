import settings, models
import logging
from datetime import datetime, date
from templatetags.management_extras import commaise
import reportlab.rl_config
reportlab.rl_config.warnOnMissingFontGlyphs = 0

from reportlab.lib.pagesizes import A4, landscape
from django.utils.translation import ugettext
from reportlab.pdfgen import canvas
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import Paragraph, SimpleDocTemplate, Image, Spacer, Frame, Table, PageBreak
from reportlab.platypus.tables import TableStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib import colors
from reportlab.lib.enums import *
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
styleRow9 = ParagraphStyle('sumRow', fontName='David',fontSize=9, leading=15)
styleSumRow = ParagraphStyle('Row', fontName='David-Bold',fontSize=11, leading=15)
styleSubj = ParagraphStyle('subject', fontName='David',fontSize=16, leading=15, alignment=TA_CENTER)
styleSubTitleBold = ParagraphStyle('subtitle', fontName='David-Bold', fontSize=15, alignment=TA_CENTER)
styleSubTitle = ParagraphStyle('subtitle', fontName='David', fontSize=15, alignment=TA_CENTER)
saleTableStyle = TableStyle(
                            [('FONTNAME', (0,0), (-1,0), 'David-Bold'),
                             ('FONTNAME', (0,1), (-1,-1), 'David'),
                             ('FONTSIZE', (0,0), (-1,-1), 11),
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

class EmployeeListWriter:
    def __init__(self, employees, nhemployees):
        self.employees = employees
        self.nhemployees = nhemployees
    @property
    def pages_count(self):
        x = len(self.employees) / 17 + 1
        if len(self.employees) % 17 == 0:
            x+=1
        y = len(self.nhemployees) / 17 + 1
        if len(self.nhemployees) % 17 == 0:
            y+=1
        return x+y+1
    def addLater(self, canv, doc):
        self.current_page += 1
        frame1 = Frame(50, 40, 150, 40)
        frame1.addFromList([Paragraph(log2vis(u'עמוד %s מתוך %s' % (self.current_page, self.pages_count)), 
                            ParagraphStyle('pages', fontName='David', fontSize=13,))], canv)
        frame2 = Frame(0, 680, 650, 150)
        frame2.addFromList([nhLogo(), datePara()], canv)
        frame4 = Frame(50, 20, 500, 70)
        frame4.addFromList([nhAddr()], canv)
    def addFirst(self, canv, doc):
        self.current_page = 1
        frame2 = Frame(0, 680, 650, 150)
        frame2.addFromList([nhLogo(), datePara()], canv)
        frame3 = Frame(50, 40, 150, 40)
        frame3.addFromList([Paragraph(log2vis(u'עמוד %s מתוך %s' % (self.current_page, self.pages_count)), 
                            ParagraphStyle('pages', fontName='David', fontSize=13,))], canv)
        frame4 = Frame(50, 20, 500, 70)
        frame4.addFromList([nhAddr()], canv)
    def employeeFlows(self):
        flows=[Paragraph(log2vis(u'נווה העיר - %s עובדים' % len(self.employees)), styleSubTitleBold),
               Spacer(0,10)]
        headers=[]
        for header in [u'מס"ד',u'פרטי\nשם',u'משפחה\nשם',u'טלפון',u'כתובת',u'העסקה\nתחילת',u'העסקה\nסוג',u'פרוייקטים']:
            headers.append(log2vis(header))
        headers.reverse()
        rows=[]
        i, rank_count, rank = (0,0,None)
        for e in self.employees:
            if rank != e.rank:
                row = [log2vis(unicode(e.rank)),None,None,None,None]
                row.reverse()
                rows.append(row)
                rank = e.rank
                rank_count+=1
                i+=1
            row=[e.id, log2vis(e.first_name), log2vis(e.last_name),
                 log2vis(e.phone), log2vis(e.address), log2vis(e.work_start.strftime('%d/%m/%Y')),
                 log2vis(unicode(e.employment_terms and e.employment_terms.hire_type or '---'))]
            projects = '\n'.join([log2vis(p.name) for p in e.projects.all()])
            row.append(projects)
            row.reverse()
            rows.append(row)
            i+=1
            if i % 17 == 0 or i == len(self.employees) + rank_count:
                data = [headers]
                data.extend(rows)
                t = Table(data)
                t.setStyle(saleTableStyle)
                flows.append(t)
                flows.extend([PageBreak(), Spacer(0,70)])
                rows = []
        flows.extend([Paragraph(log2vis(u'נייס האוס - %s עובדים' % len(self.nhemployees)), styleSubTitleBold),
                      Spacer(0,10)])
        headers=[]
        for header in [u'מס"ד',u'פרטי\nשם',u'משפחה\nשם',u'טלפון',u'כתובת',
                       u'העסקה\nתחילת',u'העסקה\nסוג']:
            headers.append(log2vis(header))
        headers.reverse()
        i, nhbranch_count, nhbranch = (0,0,None)
        for e in self.nhemployees:
            if e.nhbranch != nhbranch:
                row = [log2vis(unicode(e.nhbranch)), None,None,None,None]
                row.reverse()
                rows.append(row)
                nhbranch = e.nhbranch
                nhbranch_count+=1
                i+=1
            row=[e.id, log2vis(e.first_name), log2vis(e.last_name),
                 log2vis(e.phone), log2vis(e.address), log2vis(e.work_start.strftime('%d/%m/%Y')),
                 log2vis(unicode(e.employment_terms and e.employment_terms.hire_type or ''))]
            row.reverse()
            rows.append(row)
            i+=1
            if i % 17 == 0 or i == len(self.nhemployees) + nhbranch_count:
                data = [headers]
                data.extend(rows)
                t = Table(data)
                t.setStyle(saleTableStyle)
                flows.append(t)
                if i < len(self.nhemployees) + nhbranch_count:
                    flows.extend([PageBreak(), Spacer(0,70)])
                rows = []        
        return flows
    def build(self, filename):
        doc = SimpleDocTemplate(filename)
        story = [Spacer(0,40)]
        story.append(titlePara(u'מצבת עובדים'))
        story.append(Spacer(0, 10))
        story.extend(self.employeeFlows())
        doc.build(story, self.addFirst, self.addLater)
        return doc.canv

class MonthDemandWriter:
    @property
    def pages_count(self):
        count = self.demand.get_sales().count()
        if self.demand.diffs.count():
            count += self.demand.diffs.count() + 1
        if self.demand.remarks:
            count += 1
        affected_sales_count = 0
        for subSales in self.demand.get_affected_sales().values():
            affected_sales_count += subSales.count()
        base = self.signup_adds and (affected_sales_count + 17)/17 or 0
        if count <= 9:
            return base + 1
        if count <= 25:
            return base + 2
        if count <= 40:
            return base + 3
        if count <= 55:
            return base + 4
        return base + 5
    def __init__(self, demand, to_mail=False):
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
    def addLater(self, canv, doc):
        self.current_page += 1
        frame1 = Frame(50, 40, 150, 40)
        frame1.addFromList([Paragraph(log2vis(u'עמוד %s מתוך %s' % (self.current_page, self.pages_count)), 
                            ParagraphStyle('pages', fontName='David', fontSize=13,))], canv)
        frame2 = Frame(0, 680, 650, 150)
        frame2.addFromList([nhLogo(), datePara()], canv)
        if self.current_page == self.pages_count:
            frame3 = Frame(50, 40, 100, 100)
            frame3.addFromList([sigPara()], canv)
        frame4 = Frame(50, 20, 500, 70)
        frame4.addFromList([nhAddr()], canv)
    def addFirst(self, canv, doc):
        self.current_page = 1
        frame1 = Frame(300, 580, 250, 200)
        frame1.addFromList([self.toPara()], canv)
        frame2 = Frame(0, 680, 650, 150)
        frame2.addFromList([nhLogo(), datePara()], canv)
        frame3 = Frame(50, 40, 150, 40)
        frame3.addFromList([Paragraph(log2vis(u'עמוד %s מתוך %s' % (self.current_page, self.pages_count)), 
                            ParagraphStyle('pages', fontName='David', fontSize=13,))], canv)
        frame4 = Frame(50, 20, 500, 70)
        frame4.addFromList([nhAddr()], canv)        
        if self.pages_count == 1:
            frame5 = Frame(50, 40, 100, 100)
            frame5.addFromList([sigPara()], canv)
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
        flows = [tableCaption(caption=log2vis(u'נספח ב - דו"ח חסכון בהנחה')), Spacer(0,20),
                 tableCaption(caption=log2vis(u'מדד בסיס - %s' % self.demand.project.commissions.c_zilber.base_madad)),
                 Spacer(0,30)]
        headers = [log2vis(n) for n in [u'מס"ד',u'דרישה\nחודש', u'שם הרוכשים', u'ודירה\nבניין', u'חוזה\nתאריך',
                                        u'חוזה\nמחיר', u'0 דו"ח\nמחירון', u'חדש\nמדד', 
                                        u'60%\nממודד\nמחירון', u'מחיר\nהפרש', u'בהנחה\nחסכון\nשווי']]
        colWidths  =[None,None,80,None,None,None,40,40,40,40,40]
        colWidths.reverse()
        headers.reverse()
        rows = []
        i = 1
        total_prices, total_adds = 0, 0
        demand = self.demand
        base_madad = demand.project.commissions.c_zilber.base_madad
        current_madad = demand.get_madad() < base_madad and base_madad or demand.get_madad()
        while demand != None:
            prices_date = date(demand.month == 12 and demand.year+1 or demand.year, demand.month==12 and 1 or demand.month+1, 1)
            for s in demand.get_sales().filter(commission_include=True):
                i += 1
                actual_demand = s.actual_demand
                if actual_demand:
                    row = ['%s-%s' % (actual_demand.id, i),'%s/%s' % (actual_demand.month, actual_demand.year)]
                else:
                    row = [None, None]
                row.extend([log2vis(s.clients), '%s/%s' % (unicode(s.house.building), unicode(s.house)), 
                            s.sale_date.strftime('%d/%m/%y'), commaise(s.price)])
                doh0prices = s.house.versions.filter(type__id = models.PricelistType.Doh0, date__lte = prices_date)
                if doh0prices.count() > 0:
                    doh0price = doh0prices.latest().price
                    memudad = (((current_madad / base_madad) - 1) * 0.6 + 1) * doh0price
                    row.extend([commaise(doh0price), current_madad, commaise(memudad), commaise(s.price-memudad), commaise(s.zdb)])
                else:
                    row.extend([None,None,None,None,None])
                row.reverse()
                rows.append(row)
                total_prices += s.price
                total_adds += s.zdb
                if i % 17 == 0:
                    data = [headers]
                    data.extend(rows)
                    t = Table(data)
                    t.setStyle(saleTableStyle)
                    flows.extend([t, PageBreak(), Spacer(0,70)])
                    rows = []
            if demand.zilber_cycle_index() == 1:
                break
            demand = demand.get_previous_demand()
        sum_row = [None, None, None, None, None, Paragraph(commaise(total_prices), styleSumRow), None, None, None, None, 
                   Paragraph(commaise(round(total_adds)), styleSumRow)]
        sum_row.reverse()
        rows.append(sum_row)
        data = [headers]
        data.extend(rows)
        t = Table(data, colWidths)
        t.setStyle(saleTableStyle)
        flows.append(t)
        return flows
    
    def zilberAddsFlows(self):        
        logger = logging.getLogger('pdf')
        
        flows = [tableCaption(caption=log2vis(u'נספח א - הפרשי קצב מכירות לדרישה')),
                 Spacer(0,30)]
        headers = [log2vis(n) for n in [u'דרישה\nחודש', u'שם הרוכשים', u'ודירה\nבניין',u'מכירה\nתאריך', u'חוזה\nמחיר',
                                        u'בדרישה\nעמלה',u'חדשה\nעמלה', u'הפרש\nאחוז', u'בש"ח\nהפרש']]
        colWidths = [None,80,None,None,None,None,None,None,None]
        colWidths.reverse()
        headers.reverse()
        rows = []
        demand = self.demand
        while demand.zilber_cycle_index()>1:
            demand = demand.get_previous_demand()
        first_demand_sent_finish_date = demand.finish_date
        
        logger.info('first_demand_sent_finish_date: %s' % first_demand_sent_finish_date)

        i = 1
        total_prices, total_adds = 0, 0
        while demand != self.demand:
            logger.info('writing rows for demand: %s' % demand)
            sales = demand.get_sales()
            
            if sales.count() == 0:
                logger.warn('skipping demand %(demand)s - no sales', {'demand':demand})
                continue
            
            for s in sales:
                row = [log2vis('%s/%s' % (demand.month, demand.year)), clientsPara(s.clients), 
                               '%s/%s' % (unicode(s.house.building), unicode(s.house)), s.sale_date.strftime('%d/%m/%y'), 
                               commaise(s.price)]
                s.restore = False
                new_commission = s.c_final
                scd_final = s.project_commission_details.filter(commission='final')[0]
                orig_commission = models.restore_object(scd_final, first_demand_sent_finish_date).value
                if orig_commission == new_commission:
                    logger.warning('skipping sale #%(id)s - orig_commission == new_commission == %(commission)s',
                                   {'id':s.id, 'commission':orig_commission})
                    continue
                i += 1
                diff_amount = s.price_final * (new_commission - orig_commission) / 100
                
                logger.debug('commission calc details: %(vals)s',
                             {'vals':
                              {'new_commission':new_commission,'orig_commission':orig_commission,
                               's.price_final':s.price_final, 'diff_amount':diff_amount}
                              })
                
                row.extend([orig_commission, new_commission, new_commission - orig_commission, commaise(diff_amount)])
                row.reverse()
                rows.append(row)
                total_prices += s.price
                total_adds += round(diff_amount)
                if i % 17 == 0:
                    data = [headers]
                    data.extend(rows)
                    t = Table(data)
                    t.setStyle(saleTableStyle)
                    flows.extend([t, PageBreak(), Spacer(0,70)])
                    rows = []
            
            demand = demand.get_next_demand()
            
        sum_row = [None, None, None, None, Paragraph(commaise(total_prices), styleSumRow), None, None, None, 
                   Paragraph(commaise(total_adds), styleSumRow)]
        sum_row.reverse()
        rows.append(sum_row)
        data = [headers]
        data.extend(rows)
        t = Table(data, colWidths)
        t.setStyle(saleTableStyle)
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
        i = 1
        for subSales in self.demand.get_affected_sales().values():
            for s in subSales.all():
                i += 1
                singup = s.house.get_signup() 
                row = [singup.date.strftime('%d/%m/%y'), s.contractor_pay.strftime('%m/%y'), 
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
                if i % 17 == 0:
                    data = [headers]
                    data.extend(rows)
                    t = Table(data, colWidths)
                    t.setStyle(saleTableStyle)
                    flows.extend([t, PageBreak(), Spacer(0,70)])
                    rows = []
        sum_row = [None,None,None,None,None,None,None,None,None,Paragraph(commaise(total), styleSumRow)]
        sum_row.reverse()
        rows.append(sum_row)      
        data = [headers]
        data.extend(rows)
        t = Table(data, colWidths)
        t.setStyle(saleTableStyle)
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
        contract_num, discount, final, zilber = (False, False, False, False)
        if sales[0].contract_num:
            names.append(u"חוזה\nמס'")
            colWidths.append(40)
            contract_num = True
        if self.signup_adds:
            names.append(u'הרשמה\nתאריך')
            colWidths.append(None)
        names.extend([u'שם הרוכשים',u'ודירה\nבניין',u'מכירה\nתאריך', u'חוזה\nמחיר'])
        colWidths.extend([70, None,None,None])
        if self.demand.project.is_zilber():
            names.extend([u'מזומן\nהנחת', u'מפרט\nהוצאות',u'עו"ד\nשכ"ט', 
                          u'לחישוב\nמחיר',u'נוספות\nהוצאות'])
            colWidths.extend([35,35,None,None,35])
            zilber = True
        if not self.demand.project.id == 5:
            if sales[0].discount or sales[0].allowed_discount:
                names.extend([u'ניתן\nהנחה\n%',u'מותר\nהנחה\n%'])
                colWidths.extend([None,None])
                discount = True
        names.extend([u'בסיס\nעמלת\n%',u'בסיס\nעמלת\nשווי'])
        colWidths.extend([None,None])
        if self.demand.project.commissions.b_discount_save_precentage:
            names.extend([u'חסכון\nבונוס\n%',u'חסכון\nבונוס\nשווי',
                            u'סופי\nעמלה\n%',u'סופי\nעמלה\nשווי'])
            colWidths.extend([35,30,None,None])
            final = True
        colWidths.reverse()
        names.reverse()
        headers = [log2vis(name) for name in names]
        i=1
        next_break = 10
        flows = [tableCaption(), Spacer(0,10)]
        if self.signup_adds:
            flows.extend([self.signup_counts_para(), Spacer(0,10)])
        rows = []
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
                lawyer_pay = s.price_include_lawyer and (s.price - s.price_no_lawyer) or s.price * 0.015
                row.extend([None,None,commaise(lawyer_pay), commaise(s.price_final)])
                if s.include_registration == False:
                    row.append(s.house.building.project.commissions.registration_amount)
                else:
                    row.append(None)
            if discount:
                row.extend([s.discount, s.allowed_discount])
            row.extend([s.pc_base, commaise(s.pc_base_worth)])
            if final:
                row.extend([s.pb_dsp, commaise(s.pb_dsp_worth), s.c_final, commaise(s.c_final_worth)])
            row.reverse()#reportlab prints columns ltr
            rows.append(row)
            if i % next_break == 0 or i == sales.count():
                if i == sales.count():# insert column summaries if last row
                    row = [log2vis(u'סה"כ')]
                    if contract_num:
                        row.append(None)
                    if self.signup_adds:
                        row.append(None)
                    row.extend([None,Paragraph(log2vis('%s' % self.demand.get_sales().count()), styleSumRow),None])
                    row.append(Paragraph(commaise(self.demand.get_sales().total_price()), styleSumRow))
                    if zilber:
                        row.extend([None,None,None,None,None])
                    if discount:
                        row.extend([None,None])
                    if final:
                        row.extend([None,None,None,None,None,Paragraph(commaise(self.demand.sales_commission), styleSumRow)])
                    else:
                        row.extend([None,Paragraph(commaise(self.demand.sales_commission), styleSumRow)])
                    row.reverse()
                    rows.append(row)
                data = [headers]
                data.extend(rows)
                t = Table(data, colWidths)
                t.setStyle(saleTableStyle)
                flows.append(t)
                if i < sales.count():
                    flows.extend([PageBreak(), Spacer(0,70)])
                    next_break += 15
                rows = []
            i+=1
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
    def build(self, filename):
        logger = logging.getLogger('pdf')
        
        logger.info('starting build for %(demand)s', {'demand':self.demand})
        
        doc = SimpleDocTemplate(filename)
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
        if self.demand.get_sales().count() == 10:
            story.append(PageBreak())
        if self.demand.diffs.count() > 0:
            story.extend([Spacer(0, 20), self.addsPara()])
        if self.demand.project.is_zilber() and (self.demand.include_zilber_bonus() or not self.to_mail):
            story.extend([PageBreak(), Spacer(0,30)])
            story.extend(self.zilberAddsFlows())
            story.extend([PageBreak(), Spacer(0,30)])
            story.extend(self.zilberBonusFlows())
        story.extend([Spacer(0, 20), self.remarkPara()]) 
        if self.signup_adds:
            story.extend([PageBreak(), Spacer(0,30), titlePara(u'נספח א')])
            story.extend(self.signupFlows())
        doc.build(story, self.addFirst, self.addLater)
        return doc.canv

class MultipleDemandWriter:
    def __init__(self, demands, title, show_project, show_month):
        self.demands = demands
        self.title = title
        self.show_month = show_month
        self.show_project = show_project
    @property
    def pages_count(self):
        return 1
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
        headers, colWidths = [], []
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
        total_sales_amount, total_amount = 0,0
        for d in self.demands:
            row = []
            if self.show_project:
                project_name = d.project.name.count(d.project.city) > 0 and log2vis(d.project.name) or log2vis(u'%s %s' % (d.project.name, d.project.city))
                row.extend([log2vis(d.project.initiator), project_name])
            if self.show_month:
                row.append('%s/%s' % (d.month, d.year))
            row.extend([commaise(d.get_sales().total_price()), commaise(d.get_total_amount())])
            row.append(', '.join([str(i.num) for i in d.invoices.all()]))
            row.append(', '.join([commaise(i.amount) for i in d.invoices.all()]))
            row.append(', '.join([str(p.num) for p in d.payments.all()]))
            row.append(', '.join([commaise(p.amount) for p in d.payments.all()]))
            row.reverse()
            rows.append(row)
            rowHeights.append(28)
            total_sales_amount += d.get_sales().total_price()
            total_amount += d.get_total_amount()
        sumRow.extend([Paragraph(commaise(total_sales_amount), styleSumRow), 
                       Paragraph(commaise(total_amount), styleSumRow), None, None, None, None])
        sumRow.reverse()
        rows.append(sumRow)
        rowHeights.append(28)
        data = [headers]
        data.extend(rows)
        t = Table(data, colWidths, rowHeights)
        t.setStyle(projectTableStyle)
        return [t]
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
