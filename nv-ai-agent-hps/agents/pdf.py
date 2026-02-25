import json
import os
from datetime import datetime
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    Image, HRFlowable, KeepTogether
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.lib.pagesizes import A4


# Palette 
C_DARK_BLUE  = colors.HexColor("#1F4E79")
C_MID_BLUE   = colors.HexColor("#2E75B6")
C_LIGHT_BLUE = colors.HexColor("#D6E4F0")
C_ZEBRA      = colors.HexColor("#F2F7FB")
C_BORDER     = colors.HexColor("#AECCE8")
C_GREEN      = colors.HexColor("#1E7145")
C_RED        = colors.HexColor("#C00000")
C_WHITE      = colors.white

PAGE_W = A4[0]                        # 595 pt
MARGIN = 40
USABLE = PAGE_W - 2 * MARGIN         # ~515 pt  ≈ 7.15 inch

HIDDEN_KEYS = {"meta", "options", "artifacts", "hps"}


class JSONToPDFAgent:
    TARGET_FOLDER = r"C:\Users\amahmoudi\Downloads\config-master-main\nv-ai-agent-hps\goals"
    OUTPUT_FOLDER = r"C:\Users\amahmoudi\Downloads\config-master-main\nv-ai-agent-hps\pdfs"
    LOGO_PATH     = r"C:\Users\amahmoudi\Downloads\config-master-main\Logo-HPS.jpg"

    def __init__(self, output_filename="HPS_Config_Report.pdf", json_path=None):
        os.makedirs(self.OUTPUT_FOLDER, exist_ok=True)
        self.output_path = os.path.join(self.OUTPUT_FOLDER, output_filename)
        self.json_path = json_path
        self.data = None
        self.elements  = []
        self._init_styles()

    # Styles 
    def _init_styles(self):
        self.s_title = ParagraphStyle(
            "Title", fontSize=18, fontName="Helvetica-Bold",
            textColor=C_DARK_BLUE, alignment=1, spaceAfter=6
        )
        self.s_sub = ParagraphStyle(
            "Sub", fontSize=8, fontName="Helvetica",
            textColor=colors.grey, alignment=1, spaceAfter=0
        )
        self.s_sec = ParagraphStyle(
            "Sec", fontSize=11, fontName="Helvetica-Bold",
            textColor=C_DARK_BLUE, spaceBefore=2, spaceAfter=3
        )
        self.s_field = ParagraphStyle(
            "Field", fontSize=9, fontName="Helvetica-Bold", textColor=C_DARK_BLUE
        )
        self.s_val = ParagraphStyle(
            "Val", fontSize=9, fontName="Helvetica", textColor=colors.black
        )
        self.s_hdr = ParagraphStyle(
            "Hdr", fontSize=9, fontName="Helvetica-Bold", textColor=C_WHITE
        )
        self.s_sub_sec = ParagraphStyle(
            "SubSec", fontSize=9, fontName="Helvetica-Bold", textColor=C_DARK_BLUE
        )
        self.s_lim_hdr = ParagraphStyle(
            "LimHdr", fontSize=7, fontName="Helvetica-Bold",
            textColor=C_WHITE, alignment=1
        )
        self.s_lim_val = ParagraphStyle(
            "LimVal", fontSize=7.5, fontName="Helvetica",
            textColor=colors.black, alignment=1
        )
        self.s_lim_type = ParagraphStyle(
            "LimType", fontSize=7.5, fontName="Helvetica-Bold", textColor=C_DARK_BLUE
        )
        self.s_badge_ok  = ParagraphStyle(
            "BadgeOK", fontSize=10, fontName="Helvetica-Bold",
            textColor=C_GREEN, alignment=1
        )
        self.s_badge_err = ParagraphStyle(
            "BadgeErr", fontSize=10, fontName="Helvetica-Bold",
            textColor=C_RED, alignment=1
        )

    #  Helpers 
    def _fp(self, t): return Paragraph(str(t), self.s_field)
    def _vp(self, t):
        # Always show the field, use '—' for None/null/empty
        if t is None or (isinstance(t, str) and t.strip() == ""):
            return Paragraph("—", self.s_val)
        return Paragraph(str(t), self.s_val)
    def _hp(self, t): return Paragraph(str(t), self.s_hdr)

    @staticmethod
    def _bool(v):
        return "Yes  [+]" if v else "No  [-]"

    def _money(self, v, cur):
        try:    return f"{float(v):,.2f} {cur}"
        except: return f"{v} {cur}"

    # File helpers 
    def find_latest_json(self):
        if self.json_path:
            # Already set, skip finding
            return
        json_files = []
        for root, dirs, files in os.walk(self.TARGET_FOLDER):
            for f in files:
                if f.endswith(".json"):
                    json_files.append(os.path.join(root, f))
        if not json_files:
            raise FileNotFoundError("No JSON files found in goals directory.")
        self.json_path = max(json_files, key=os.path.getmtime)
        print(f"Latest JSON: {os.path.basename(self.json_path)}")

    def load_json(self):
        with open(self.json_path, "r", encoding="utf-8") as f:
            self.data = json.load(f)

    # Table builders 
    def _base_cmds(self, n_rows, hdr_rows=1):
        """Common table style commands with zebra striping."""
        cmds = [
            ("BACKGROUND",    (0, 0), (-1, hdr_rows - 1), C_DARK_BLUE),
            ("GRID",          (0, 0), (-1, -1), 0.4, C_BORDER),
            ("VALIGN",        (0, 0), (-1, -1), "TOP"),
            ("LEFTPADDING",   (0, 0), (-1, -1), 5),
            ("RIGHTPADDING",  (0, 0), (-1, -1), 5),
            ("TOPPADDING",    (0, 0), (-1, -1), 4),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ]
        for i in range(hdr_rows, n_rows):
            bg = C_WHITE if i % 2 == 0 else C_ZEBRA
            cmds.append(("BACKGROUND", (0, i), (-1, i), bg))
        return cmds

    def _kv_table(self, rows, col_w=None):
        """
        Key-value table. rows = list of (key, value) or ("__section__", label).
        col_w defaults to [2.5in, rest].
        """
        if col_w is None:
            col_w = [2.5 * inch, USABLE - 2.5 * inch]

        data  = [[self._hp("Field"), self._hp("Value")]]
        cmds  = self._base_cmds(1)           # will extend as we add rows

        for i, (k, v) in enumerate(rows, start=1):
            if k == "__section__":
                data.append([Paragraph(f"<b>{v}</b>", self.s_sub_sec), ""])
                cmds += [
                    ("BACKGROUND",   (0, i), (-1, i), C_LIGHT_BLUE),
                    ("SPAN",         (0, i), (-1, i)),
                    ("TOPPADDING",   (0, i), (-1, i), 5),
                    ("BOTTOMPADDING",(0, i), (-1, i), 5),
                ]
            else:
                bg = C_WHITE if i % 2 == 0 else C_ZEBRA
                data.append([self._fp(k), self._vp(v)])
                cmds.append(("BACKGROUND", (0, i), (-1, i), bg))

        t = Table(data, colWidths=col_w, repeatRows=1)
        t.setStyle(TableStyle(cmds))
        return t

    def _limits_table(self, by_type, currency):
        """
        Limits rendered as a landscape-friendly vertical table.
        Rows = metrics, Columns = limit types.
        This avoids horizontal overflow on A4.
        """
        # periods and their metrics
        PERIOD_META = [
            ("Domestic",       "domestic",        ["daily_amount","daily_count","weekly_amount","weekly_count","monthly_amount","monthly_count"]),
            ("International",  "international",   ["daily_amount","daily_count","weekly_amount","weekly_count","monthly_amount","monthly_count"]),
            ("Total",          "total",           ["daily_amount","daily_count","weekly_amount","weekly_count","monthly_amount","monthly_count"]),
            ("Per Transaction","per_transaction",  ["min_amount","max_amount"]),
        ]
        METRIC_LABEL = {
            "daily_amount":"Daily Amt","daily_count":"Daily Cnt",
            "weekly_amount":"Weekly Amt","weekly_count":"Weekly Cnt",
            "monthly_amount":"Monthly Amt","monthly_count":"Monthly Cnt",
            "min_amount":"Min Amt","max_amount":"Max Amt",
        }
        IS_AMOUNT = {"daily_amount","weekly_amount","monthly_amount",
                     "min_amount","max_amount"}

        limit_types = list(by_type.keys())
        n_lt = len(limit_types)

        # Column widths: metric label col + one col per limit type
        lbl_w  = 1.5 * inch
        val_w  = (USABLE - lbl_w) / max(n_lt, 1)
        col_w  = [lbl_w] + [val_w] * n_lt

        # Header row
        hdr = [self._hp("Metric")] + [self._hp(lt) for lt in limit_types]
        data = [hdr]
        cmds = [
            ("BACKGROUND",    (0, 0), (-1, 0), C_MID_BLUE),
            ("GRID",          (0, 0), (-1, -1), 0.4, C_BORDER),
            ("VALIGN",        (0, 0), (-1, -1), "MIDDLE"),
            ("ALIGN",         (1, 0), (-1, -1), "CENTER"),
            ("LEFTPADDING",   (0, 0), (-1, -1), 4),
            ("RIGHTPADDING",  (0, 0), (-1, -1), 4),
            ("TOPPADDING",    (0, 0), (-1, -1), 3),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
        ]

        row_i = 1
        for period_label, period_key, metrics in PERIOD_META:
            # Period section row
            p_cell = Paragraph(f"<b>{period_label}</b>", self.s_sub_sec)
            data.append([p_cell] + [""] * n_lt)
            cmds += [
                ("BACKGROUND", (0, row_i), (-1, row_i), C_LIGHT_BLUE),
                ("SPAN",       (0, row_i), (-1, row_i)),
                ("TOPPADDING", (0, row_i), (-1, row_i), 4),
                ("BOTTOMPADDING",(0,row_i),(-1, row_i), 4),
            ]
            row_i += 1

            for m in metrics:
                bg = C_WHITE if row_i % 2 == 0 else C_ZEBRA
                row = [Paragraph(METRIC_LABEL[m], self.s_lim_type)]
                for lt in limit_types:
                    raw = by_type.get(lt, {}).get(period_key, {}).get(m, "—")
                    if raw != "—" and m in IS_AMOUNT:
                        cell = self._money(raw, currency)
                    else:
                        cell = str(raw)
                    row.append(Paragraph(cell, self.s_lim_val))
                data.append(row)
                cmds.append(("BACKGROUND", (0, row_i), (-1, row_i), bg))
                row_i += 1

        t = Table(data, colWidths=col_w, repeatRows=1)
        t.setStyle(TableStyle(cmds))
        return t

    # Section title 
    def _sec_title(self, text):
        self.elements.append(Spacer(1, 0.15 * inch))
        self.elements.append(HRFlowable(
            width="100%", thickness=1, color=C_BORDER, spaceAfter=4
        ))
        self.elements.append(Paragraph(text, self.s_sec))

    # Header block 
    def _add_header(self, case_id, generated_at):
        if os.path.exists(self.LOGO_PATH):
            logo = Image(self.LOGO_PATH, width=1.5 * inch, height=0.8 * inch)
            logo.hAlign = "CENTER"
            self.elements.append(logo)
            self.elements.append(Spacer(1, 0.12 * inch))

        self.elements.append(Paragraph("HPS Configuration Report", self.s_title))
        self.elements.append(Spacer(1, 0.06 * inch))          # gap between title & subtitle
        self.elements.append(Paragraph(
            f"Case ID: <b>{case_id}</b>  |  Generated: {generated_at}", self.s_sub
        ))
        self.elements.append(Spacer(1, 0.1 * inch))
        self.elements.append(HRFlowable(
            width="100%", thickness=1.5, color=C_DARK_BLUE, spaceAfter=6
        ))

    # Status badge 
    def _add_status_badge(self, status):
        ok = status.get("is_valid") and status.get("is_complete")
        label  = "[OK]  Complete & Valid" if ok else "[!!]  Incomplete / Invalid"
        style  = self.s_badge_ok if ok else self.s_badge_err
        self.elements.append(Spacer(1, 0.05 * inch))
        self.elements.append(Paragraph(label, style))

    # Section renderers 
    def _add_bank_section(self, bank):
        self._sec_title(">> Bank Information")
        rows = [
            ("Bank Name", bank.get("name",      "—")),
            ("Country",   bank.get("country",   "—")),
            ("Currency",  bank.get("currency",  "—")),
            ("Bank Code", bank.get("bank_code", "—")),
            ("Resources", ", ".join(bank.get("resources", []))),
        ]
        self.elements.append(self._kv_table(rows))

    def _add_agencies_section(self, agencies):
        self._sec_title(">> Agencies")
        rows = []
        for i, ag in enumerate(agencies):
            rows.append(("__section__", f"Agency {i + 1}"))
            rows += [
                ("Name",        ag.get("agency_name", "—")),
                ("Code",        ag.get("agency_code", "—")),
                ("City",        ag.get("city",        "—")),
                ("City Code",   ag.get("city_code",   "—")),
                ("Region",      ag.get("region",      "—")),
                ("Region Code", ag.get("region_code", "—")),
            ]
        self.elements.append(self._kv_table(rows))

    def _add_cards_section(self, cards, currency):
        for ci, card in enumerate(cards):
            desc = card.get("card_info", {}).get("card_description", f"Card {ci+1}")
            self._sec_title(f">> Card {ci + 1}  --  {desc}")

            info = card.get("card_info", {})
            rng  = card.get("card_range", {})
            fees = card.get("fees", {})
            svcs = card.get("services", {}).get("enabled", [])
            limits = card.get("limits", {})
            selected_lt = limits.get("selected_limit_types", [])

            rows = [
                ("__section__", "Card Info"),
                ("BIN",              info.get("bin",             "—")),
                ("Description",      info.get("card_description","—")),
                ("Network",          info.get("network",         "—")),
                ("Plastic Type",     info.get("plastic_type",    "—")),
                ("Product Type",     info.get("product_type",    "—")),
                ("Product Code",     info.get("product_code",    "—")),
                ("Service Code",     info.get("service_code",    "—")),
                ("PVK Index",        info.get("pvk_index",       "—")),
                ("Expiration (yrs)", info.get("expiration",      "—")),
                ("Renewal Option",   self._bool(info.get("renewal_option") == "Y")),
                ("Pre-Expiration",   info.get("pre_expiration",  "—")),

                ("__section__", "Card Range"),
                ("Start Range", rng.get("start_range", "—")),
                ("End Range",   rng.get("end_range",   "—")),

                ("__section__", "Fees"),
                ("Description",          fees.get("fee_description",     "—")),
                ("Billing Event",         fees.get("billing_event",       "—")),
                ("Grace Period (days)",   fees.get("grace_period",        "—")),
                ("Billing Period (mo)",   fees.get("billing_period",      "—")),
                ("Registration Fee",      self._money(fees.get("registration_fee",     0), currency)),
                ("Periodic Fee",          self._money(fees.get("periodic_fee",         0), currency)),
                ("Replacement Fee",       self._money(fees.get("replacement_fee",      0), currency)),
                ("PIN Recalculation Fee", self._money(fees.get("pin_recalculation_fee",0), currency)),

                ("__section__", "Enabled Services"),
                ("Services", ", ".join(svcs) if svcs else "—"),

                ("__section__", "Limits"),
                ("Limit Types", ", ".join(selected_lt) if selected_lt else "—"),
            ]
            self.elements.append(self._kv_table(rows))

            # Limits detail — separate table below
            by_type = limits.get("by_type", {})
            if by_type:
                self.elements.append(Spacer(1, 0.1 * inch))
                self.elements.append(Paragraph(
                    "<b>Transaction Limits Detail</b>",
                    ParagraphStyle("lbl", fontSize=9, fontName="Helvetica-Bold",
                                   textColor=C_DARK_BLUE, spaceAfter=4)
                ))
                self.elements.append(self._limits_table(by_type, currency))

    def _add_status_section(self, status):
        self._sec_title(">> Report Status")
        missing = status.get("missing_fields", [])
        errors  = status.get("errors", [])
        rows = [
            ("Complete",       self._bool(status.get("is_complete", False))),
            ("Valid",          self._bool(status.get("is_valid",    False))),
            ("Missing Fields", ", ".join(missing) if missing else "None"),
            ("Errors",         ", ".join(errors)  if errors  else "None"),
        ]
        self.elements.append(self._kv_table(rows))

    
    def run(self):
        print("Starting execution...")
        self.find_latest_json()
        self.load_json()

        raw_data = self.data
        status_data = raw_data.get("status", {})

        # Support state.json structure: facts + meta
        if "facts" in raw_data and isinstance(raw_data.get("facts"), dict):
            data = raw_data.get("facts", {})
            meta = raw_data.get("meta", {})
            if not status_data:
                status_data = {
                    "is_complete": bool(raw_data.get("done")),
                    "is_valid": bool(raw_data.get("done")),
                    "missing_fields": [],
                    "errors": [],
                }
            case_id = raw_data.get("case_id", meta.get("goal_id", "N/A"))
        else:
            data = raw_data
            case_id = data.get("case_id", "N/A")

        currency  = data.get("bank", {}).get("currency", "")
        generated = datetime.now().strftime("%Y-%m-%d  %H:%M:%S")

        doc = SimpleDocTemplate(
            self.output_path, pagesize=A4,
            rightMargin=MARGIN, leftMargin=MARGIN,
            topMargin=MARGIN,   bottomMargin=MARGIN
        )

        self._add_header(case_id, generated)
        self._add_status_badge(status_data)
        self._add_bank_section(data.get("bank", {}))
        self._add_agencies_section(data.get("bank", {}).get("agencies", []))
        self._add_cards_section(data.get("cards", []), currency)
        self._add_status_section(status_data)

        print("Generating PDF...")
        doc.build(self.elements)
        print(f"PDF created: {self.output_path}")


if __name__ == "__main__":
    agent = JSONToPDFAgent("HPS_Config_Report.pdf")
    agent.run()