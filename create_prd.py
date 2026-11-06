from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_CELL_VERTICAL_ALIGNMENT
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.enum.section import WD_SECTION

OUT='個人行程與任務管理系統_PRD.docx'
doc=Document()
sec=doc.sections[0]
sec.top_margin=Inches(.7); sec.bottom_margin=Inches(.7); sec.left_margin=Inches(.78); sec.right_margin=Inches(.78)
styles=doc.styles
for name in ['Normal','Title','Heading 1','Heading 2','Heading 3']:
    st=styles[name]
    st.font.name='Aptos'
    st._element.rPr.rFonts.set(qn('w:eastAsia'),'Microsoft JhengHei')
styles['Normal'].font.size=Pt(10.5); styles['Normal'].font.color.rgb=RGBColor(52,61,56)
styles['Normal'].paragraph_format.space_after=Pt(5)
styles['Title'].font.size=Pt(28); styles['Title'].font.bold=True; styles['Title'].font.color.rgb=RGBColor(51,73,62)
styles['Heading 1'].font.size=Pt(17); styles['Heading 1'].font.bold=True; styles['Heading 1'].font.color.rgb=RGBColor(73,104,87)
styles['Heading 1'].paragraph_format.space_before=Pt(14); styles['Heading 1'].paragraph_format.space_after=Pt(6)
styles['Heading 2'].font.size=Pt(12.5); styles['Heading 2'].font.bold=True; styles['Heading 2'].font.color.rgb=RGBColor(74,92,82)
styles['Heading 2'].paragraph_format.space_before=Pt(8); styles['Heading 2'].paragraph_format.space_after=Pt(4)

def shade(cell,color):
    tcPr=cell._tc.get_or_add_tcPr(); shd=OxmlElement('w:shd'); shd.set(qn('w:fill'),color); tcPr.append(shd)
def set_cell(cell,text,bold=False,color=None,size=9.2):
    cell.text=''; p=cell.paragraphs[0]; p.paragraph_format.space_after=Pt(1); r=p.add_run(str(text)); r.bold=bold; r.font.size=Pt(size); r.font.name='Aptos'; r._element.rPr.rFonts.set(qn('w:eastAsia'),'Microsoft JhengHei')
    if color:r.font.color.rgb=RGBColor(*color)
    cell.vertical_alignment=WD_CELL_VERTICAL_ALIGNMENT.CENTER

def table(headers,rows,widths=None):
    t=doc.add_table(rows=1,cols=len(headers)); t.alignment=WD_TABLE_ALIGNMENT.CENTER; t.style='Table Grid'; t.autofit=False
    for i,h in enumerate(headers): set_cell(t.rows[0].cells[i],h,True,(255,255,255),9);shade(t.rows[0].cells[i],'526E5D')
    for row in rows:
        cells=t.add_row().cells
        for i,v in enumerate(row):
            set_cell(cells[i],v)
            if len(t.rows)%2==0:shade(cells[i],'F2F5F2')
    if widths:
        for row in t.rows:
            for i,w in enumerate(widths):row.cells[i].width=Inches(w)
    doc.add_paragraph().paragraph_format.space_after=Pt(0)
    return t

def bullet(text):
    p=doc.add_paragraph(style='List Bullet');p.paragraph_format.space_after=Pt(2);p.add_run(text);return p

def numbered(text):
    p=doc.add_paragraph(style='List Number');p.paragraph_format.space_after=Pt(2);p.add_run(text);return p

# running header/footer
header=sec.header.paragraphs[0];header.alignment=WD_ALIGN_PARAGRAPH.RIGHT
r=header.add_run('產品需求文件  /  個人效率工具');r.font.size=Pt(8);r.font.color.rgb=RGBColor(128,143,133)
footer=sec.footer.paragraphs[0];footer.alignment=WD_ALIGN_PARAGRAPH.CENTER
r=footer.add_run('產品需求文件　•　版本 1.0　•　2026-10-30');r.font.size=Pt(8);r.font.color.rgb=RGBColor(128,143,133)

p=doc.add_paragraph(style='Title');p.add_run('個人行程與任務管理系統')
p=doc.add_paragraph();r=p.add_run('產品需求文件  |  PRD');r.bold=True;r.font.size=Pt(13);r.font.color.rgb=RGBColor(111,137,121)
p=doc.add_paragraph();p.paragraph_format.space_after=Pt(12);r=p.add_run('版本 1.0　·　需求狀態：初步需求已確認，待技術與營運細節補充');r.font.size=Pt(9);r.font.color.rgb=RGBColor(119,131,123)
doc.add_heading('文件目的',level=1)
doc.add_paragraph('本文件將已討論的需求整理為可供產品、設計與工程團隊共同評估的產品基準。產品目標是讓個人使用者在同一個工作空間中規劃行程、記錄待辦、追蹤長期專案，並以工作與私人分類協調生活安排。')
table(['欄位','內容'],[['產品','個人行程與任務管理系統'],['主要使用者','需要安排工作與私人生活、管理日常任務並推進長期目標的個人使用者'],['主要裝置','桌面與手機皆需支援，採響應式介面'],['視覺方向','簡潔、低飽和色系；自訂分類顏色負責辨識，不讓色彩干擾閱讀'],['文件依據','使用者訪談討論及目前互動式 HTML 前端原型']],[1.45,5.7])

doc.add_heading('1. 產品概述',level=1)
doc.add_paragraph('系統以行事曆、待辦清單與專案追蹤為核心。使用者可在同一個空間中查看有明確時間的行程、尚未排時段的任務，以及專案的進度與里程碑。工作、私人及其他自訂分類共用同一行事曆，並以自訂顏色與篩選降低資訊混雜。')
doc.add_heading('1.1 產品目標',level=2)
for x in ['快速掌握本週安排與今天待辦，減少在不同工具間切換。','支援從單純待辦到時間區塊的不同規劃深度，避免未排程任務塞滿行事曆。','將長期目標拆解為階段與里程碑，透過進度與下一步維持推進感。','桌面提供高效率的整週規劃；手機提供可觸控操作的行程檢視與快速管理。']:bullet(x)
doc.add_heading('1.2 非目標與原型界線',level=2)
doc.add_paragraph('目前原型是單頁前端互動示範，資料僅存於瀏覽器頁面執行期間。雲端同步、帳號與權限、跨裝置持久化、提醒通知、多人共用、外部行事曆整合及正式資料備份尚未定義，不應視為已承諾的第一版功能。')

doc.add_heading('2. 使用者與核心情境',level=1)
table(['情境','使用者需求','系統支援'],[['每日規劃','查看本週時間安排，找出今天優先事項','週行事曆、今天待辦、工作／私人篩選'],['隨手記錄','先記下一件事，不必立即決定時間','建立僅勾選任務，或指定日期但不指定時段'],['安排時段','把需在特定時間進行的工作放入日曆','行程設定日期、開始時間與結束時間'],['推進長期目標','掌握專案期限、完成比例與下一步','專案目標日期、進度、下一步及可操作里程碑'],['管理生活範疇','依不同生活領域辨識與檢視事項','自訂分類名稱與顏色，並可篩選行程']],[1.15,2.75,3.25])

doc.add_heading('3. 資訊架構與導覽',level=1)
for x in ['行事曆：主要規劃畫面，預設週視圖；側欄／輔助區顯示今日待辦及進行中的專案。','待辦事項：集中查看任務、完成狀態、日期與分類。','專案：查看目標日期、完成進度、下一步與階段／里程碑。','我的分類：管理自訂分類，新增、重新命名、選擇顏色及刪除。','新增入口：建立待辦、行程或專案，依項目類型顯示對應欄位。']:bullet(x)

doc.add_heading('4. 功能需求',level=1)
doc.add_heading('4.1 行事曆與行程',level=2)
table(['ID','需求','優先級','驗收條件'],[['CAL-01','提供週行事曆檢視，顯示一週日期與時間軸。','Must','可辨識週範圍、每日日期及有時間行程。'],['CAL-02','行程包含名稱、日期、開始時間、結束時間與分類。','Must','儲存後出現在指定日期與時間位置。'],['CAL-03','可按分類篩選行程，至少提供全部與各自訂分類。','Must','選取分類後僅顯示該類行程；選全部恢復。'],['CAL-04','行程可刪除，刪除前要求確認。','Must','確認後從行事曆移除；取消則保持原狀。'],['CAL-05','週行程區在固定視窗中可上下、左右拖曳瀏覽。','Must','不需整頁延伸；滑鼠及觸控操作可移動行程內容。'],['CAL-06','保留日／週／月視圖切換入口。','Should','初版需明確界定日、月視圖是否納入；目前原型只有週視圖實際呈現。']],[.65,2.6,.75,3.15])
doc.add_heading('4.2 待辦任務',level=2)
table(['ID','需求','優先級','驗收條件'],[['TASK-01','任務至少支援名稱、完成狀態、分類及可選日期。','Must','日期可留空或指定日期；指定日期不要求時間。'],['TASK-02','可直接勾選／取消完成。','Must','狀態切換後完成樣式與未完成數量同步。'],['TASK-03','建立有日期與起訖時間的事項時，可作為行事曆行程呈現。','Must','建立後出現在日曆，日期與時間正確。'],['TASK-04','任務可刪除並於刪除前確認。','Must','確認刪除後任務從清單消失；取消不變。'],['TASK-05','提供今日任務摘要及完整任務清單。','Should','今日摘要僅列當日任務，全部清單可檢視其他日期任務。']],[.65,2.6,.75,3.15])
doc.add_heading('4.3 專案、進度與里程碑',level=2)
table(['ID','需求','優先級','驗收條件'],[['PROJ-01','專案包含名稱、目標日期、進度、下一步任務及階段／里程碑。','Must','建立專案後在專案清單與追蹤區呈現必要資訊。'],['PROJ-02','里程碑可點選完成或恢復未完成。','Must','互動後完成狀態、百分比與下一步立即更新。'],['PROJ-03','使用者可直接輸入 0–100 的進度。','Should','非法值拒絕；合法值更新進度條與文字。'],['PROJ-04','專案可刪除，刪除前要求確認。','Must','確認後自專案與里程碑檢視移除。'],['PROJ-05','進度計算規則需保持一致。','Must','建議里程碑式專案以完成數／總數計算；手動調整進度時需定義與里程碑狀態的同步規則。']],[.65,2.6,.75,3.15])
doc.add_heading('4.4 分類與顏色',level=2)
table(['ID','需求','優先級','驗收條件'],[['TAG-01','分類可新增自訂名稱與顏色。','Must','新增後出現在分類清單、篩選器及任務／行程表單。'],['TAG-02','分類可編輯名稱與顏色。','Must','變更後所有使用該分類的行程及任務同步更新。'],['TAG-03','分類可刪除，並先顯示確認。','Must','確認刪除後移除分類；已指派項目改為未分類。'],['TAG-04','提供預設低飽和色票及自訂色彩選擇器。','Must','預設色票可點擊，選取狀態可見；可選取自訂色。'],['TAG-05','標籤顏色應一致套用於分類標記與相關行程呈現。','Should','色彩語意一致且文字對比可讀。']],[.65,2.6,.75,3.15])

doc.add_heading('5. 主要使用流程',level=1)
doc.add_heading('5.1 新增有時間行程',level=2)
for x in ['使用者點選新增，選擇「行程」。','輸入名稱、日期、開始／結束時間與分類。','儲存後行程出現在行事曆對應日期和時段，可透過分類篩選。']:numbered(x)
doc.add_heading('5.2 記錄待辦並安排日期',level=2)
for x in ['使用者建立待辦，輸入名稱與分類。','可選擇指定日期；若暫時未安排，日期可留空。','在待辦清單勾選完成；如需安排具體時段，改建立行程／時間區塊。']:numbered(x)
doc.add_heading('5.3 管理專案進度',level=2)
for x in ['建立專案並填入目標日期與里程碑。','點選里程碑更新完成狀態；系統同步計算進度與下一步。','必要時直接編輯進度數字；里程碑和手動進度之間的同步規則須在實作前決定。']:numbered(x)
doc.add_heading('5.4 管理自訂分類',level=2)
for x in ['新增分類並輸入自訂名稱。','點選預設色票或開啟色彩選擇器選擇顏色，儲存後套用。','編輯分類可更新既有項目；刪除分類需確認，既有項目改為未分類。']:numbered(x)

doc.add_heading('6. 介面與互動原則',level=1)
for x in ['視覺：清爽、中性底色、低飽和分類色；主要操作按鈕清晰但不搶佔內容。','桌面：左側導覽；行事曆主區與今日待辦／專案摘要並列。','手機：改用底部主要導覽；避免整個頁面被週行程高度撐長，行事曆自身可觸控拖移。','可操作性：刪除需二次確認；完成狀態、篩選與顏色選取需有清楚的視覺回饋。','可及性：互動元素需有可辨識文字或 aria-label、鍵盤焦點、足夠點擊區域；顏色不可作為唯一資訊表達方式。']:bullet(x)

doc.add_heading('7. 非功能需求',level=1)
table(['面向','初步要求'],[['響應式','支援桌面及手機主要尺寸；內容不應超出視窗，核心操作可觸控。'],['效能','週行事曆與清單在一般個人資料量下應快速呈現；大型資料量上限待定。'],['資料持久性','目前原型重整頁面即遺失新增資料。產品版本應決定本機儲存或帳戶雲端同步及備份策略。'],['隱私與安全','行程與任務可能包含個人敏感資訊；帳號、加密、資料保留與刪除政策待定。'],['可維護性','分類名稱與顏色應以資料模型管理，避免硬編碼在介面模板。']],[1.35,5.8])

doc.add_heading('8. 資料概念模型',level=1)
table(['實體','主要欄位','關聯／規則'],[['分類 Tag','id、name、color','一個分類可被多筆任務與行程引用；刪除時依產品規則轉未分類。'],['任務 Task','id、title、dueDate?、completed、tagId?、projectId?','日期與專案關聯可選；任務完成狀態獨立。'],['行程 Event','id、title、date、startTime、endTime、tagId?','必須有日期與時間區間；在日曆時間軸顯示。'],['專案 Project','id、name、targetDate、progress、nextAction','包含多個里程碑；是否將任務關聯為下一步待辦需確認。'],['里程碑 Milestone','id、projectId、title、order、completed','屬於單一專案；建議依完成數計算進度。']],[1.15,2.5,3.5])

doc.add_heading('9. 衡量指標',level=1)
doc.add_paragraph('上線後建議評估以下指標，實際基準與目標值需在試用／測試階段設定：')
for x in ['週活躍使用者中完成每週規劃的比例。','任務建立後完成率與逾期率。','專案建立後至少更新一次里程碑／進度的比例。','分類篩選、拖移瀏覽等核心互動的成功率與可用性回饋。','跨裝置使用時資料一致性、同步失敗率（若納入雲端同步）。']:bullet(x)

doc.add_heading('10. 範圍優先級與版本建議',level=1)
table(['版本','建議範圍','備註'],[['MVP','響應式行事曆週視圖、時間行程、待辦與勾選、專案與里程碑、分類自訂／顏色／刪除、資料持久化、編輯與刪除','目前需求的最小可用產品；資料持久化為必要產品決策。'],['後續版本','日／月視圖、拖放任務排程、提醒通知、重複行程、搜尋、外部行事曆整合、匯出／備份','依使用者驗證與技術成本排序。'],['待釐清','帳戶與雲端同步、隱私與備份、提醒通路、專案與任務關聯、刪除保留政策、時區與週起始日','需於正式估工前決定。']],[1.0,3.7,2.45])

doc.add_heading('11. 假設、限制與待決問題',level=1)
for x in ['目前採週一為週行事曆的起始日；是否提供週起始日設定尚未確認。','目前討論以單人個人工作空間為前提；是否需多帳戶、家庭／團隊共享尚未確認。','專案目前可輸入里程碑並操作進度；專案任務是否直接連結待辦尚未定義。','手動指定專案進度是否應同步調整里程碑完成狀態，需明確決策。','刪除分類後，項目改為「未分類」是原型建議行為，正式產品仍需確認。','新增、修改、刪除與分類自訂目前只在頁面記憶體中有效；正式版本須選定資料儲存方式。','時間軸目前呈現 08:00 至 18:00 的示範範圍；全天事件、跨日事件與可調整時間範圍尚未規格化。','目前 UI 有日／月視圖入口，但未實際實作；需決定納入 MVP 或明確標示為後續功能。']:bullet(x)

doc.add_heading('附錄 A 原型涵蓋狀態',level=1)
table(['項目','原型狀態'],[['週行事曆、分類篩選、區域拖曳瀏覽','已提供互動示範；拖曳為日曆視窗內捲動。'],['新增行程、待辦、專案','已提供；新增資料目前不持久化。'],['任務完成、刪除行程／任務／專案','已提供互動操作。'],['里程碑與進度調整','里程碑可切換；進度可手動輸入。同步規則需進一步完善。'],['分類新增、名稱／顏色編輯、刪除','已提供互動示範；色票選擇器正進行修正與驗證。'],['手機響應式版面','已提供樣式；仍需真機與多瀏覽器測試。']],[2.55,4.6])

doc.save(OUT)
print(OUT)
