
from celldown import CellDown
from super_xlookup import SuperXlookup
from ticket import Ticket


reference_date  = "11/06/2026"



xl2 = SuperXlookup(
        source_file_path=r"C:\Users\f50056342\Desktop\computer science\NUR Project Lyne\inputs\Book1.xlsx",
        target_file_path=r"C:\Users\f50056342\Desktop\my work\OCM RAN\OCM RAN INCIDENT FOLOW-UP 12-06-2026 18H UTC.xlsx",
        source_key_column="Codesite",
        target_key_column=["Site ID", "SITE_ID", "site id"],  # Liste de noms possibles
        target_value_column=["Actions en cours", "Action en cours", "Actions"],
        result_position_column="last_column",
        result_column_name=f"OCM RAN  UTC",
        source_sheet_name="Sheet1",
        target_sheet_name="ALL SITES DOWN",
        reference_name="OCM RAN",

    )
xl2.run()

xl2 = SuperXlookup(
        source_file_path=r"C:\Users\f50056342\Desktop\computer science\NUR Project Lyne\inputs\Book1.xlsx",
        target_file_path=r"C:\Users\f50056342\Desktop\my work\OCM RAN\OCM RAN INCIDENT FOLOW-UP 12-06-2026 13H UTC.xlsx",
        source_key_column="Codesite",
        target_key_column=["Site ID", "SITE_ID", "site id"],  # Liste de noms possibles
        target_value_column=["Actions en cours", "Action en cours", "Actions"],
        result_position_column="last_column",
        result_column_name=f"OCM RAN  UTC",
        source_sheet_name="Sheet1",
        target_sheet_name="ALL SITES DOWN",
        reference_name="OCM RAN",

    )
xl2.run()


xl2 = SuperXlookup(
        source_file_path=r"C:\Users\f50056342\Desktop\computer science\NUR Project Lyne\inputs\Book1.xlsx",
        target_file_path=r"C:\Users\f50056342\Desktop\my work\OCM RAN\OCM RAN INCIDENT FOLOW-UP 12-06-2026 11H UTC.xlsx",
        source_key_column="Codesite",
        target_key_column=["Site ID", "SITE_ID", "site id"],  # Liste de noms possibles
        target_value_column=["Actions en cours", "Action en cours", "Actions"],
        result_position_column="last_column",
        result_column_name=f"OCM RAN  UTC",
        source_sheet_name="Sheet1",
        target_sheet_name="ALL SITES DOWN",
        reference_name="OCM RAN",

    )
xl2.run()



ticket = Ticket(
        source_file_path=r"C:\Users\f50056342\Desktop\computer science\NUR Project Lyne\inputs\Book1.xlsx",
        target_file_path=r"C:\Users\f50056342\Downloads\Incident Ticket_20260614162016.xlsx",
        source_key_column="Codesite",
        result_position_column="last_column",
        result_column_name="Ticket",
        source_sheet_name="Sheet1",
        target_sheet_name="",
        reference_name="Ticket",
        target_join_columns=[
            ["Ticket ID", "Ticket ID(Create TT)"],
            ["Description", "Description(Process TT)"],
            ["Solution", "Solution(Process TT)"],
            ["Root Cause", "Root Cause(Process TT)"],
            ["Incident Reason", "Incident Reason Detail(Process TT)"]
        ],
        join_separator="..",
        ignore_empty=True,
        # --- Extraction de la clé cible ---
        extract_source_column=["Site Name", "Site ID", "SITE_ID", "site id", "site_code", "site code"],  # Liste de noms possibles pour la clé cible
        # target_key_column=None (extraction auto)
    )

ticket.run()

celldown = CellDown(
    source_file_path=r"C:\Users\f50056342\Desktop\computer science\NUR Project Lyne\inputs\Book1.xlsx",
    target_file_path=r"C:\Users\f50056342\Desktop\my work\cellsdow files\celldown Nokia\DAILY_W24_CELLS_DOWN_NOKIA_0806 AU 13062026 14h14.xlsx",
    colown_key_path_source="Codesite",
    target_key_column=["Site Code", "SITE_CODE", "site code", "Code Site"],
    target_value_column=["Comment", "COMMENT", "comment"],
    result_position_column="last_column",
    source_sheet_path="Sheet1",
    date_str="12062026",
    reference_name="CellDown Nokia",
    reference_date=reference_date
)
celldown.super_xlookup_par_date()

celldown = CellDown(
    source_file_path=r"C:\Users\f50056342\Desktop\computer science\NUR Project Lyne\inputs\Book1.xlsx",
    target_file_path=r"C:\Users\f50056342\Desktop\my work\cellsdow files\celldown Huawei\DAILY_W24_CELLS_DOWN_HUAWEI_13062026 14h.xlsx",
    colown_key_path_source="Codesite",
    target_key_column=["Site Code", "SITE_CODE", "site code", "Code Site"],
    target_value_column=["Comment", "COMMENT", "comment"],
    result_position_column="last_column",
    source_sheet_path="Sheet1",
    date_str="12062026",
    reference_name="CellDown Huawei",
    reference_date=reference_date
)
celldown.super_xlookup_par_date()

celldown = CellDown(
    source_file_path=r"C:\Users\f50056342\Desktop\computer science\NUR Project Lyne\inputs\Book1.xlsx",
    target_file_path=r"C:\Users\f50056342\Desktop\my work\cellsdow files\celldown zte\DAILY_W24_CELLS_DOWN_ZTE_AU 0806 au 13062026 14h.xlsx",
    colown_key_path_source="Codesite",
    target_key_column=["Site Code", "SITE_CODE", "site code", "Code Site"],
    target_value_column=["Comment", "COMMENT", "comment"],
    result_position_column="last_column",
    source_sheet_path="Sheet1",
    date_str="12062026",
    reference_name="CellDown ZTE",  
    reference_date=reference_date
)
celldown.super_xlookup_par_date()