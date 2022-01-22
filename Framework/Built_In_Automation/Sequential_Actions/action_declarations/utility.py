declarations = (
    {"name": "math", "function": "Calculate", "screenshot": "none"},
    {"name": "upload", "function": "Upload", "screenshot": "none"},
    {"name": "save string", "function": "Save_Text", "screenshot": "none"},
    {"name": "copy", "function": "Copy_File_or_Folder", "screenshot": "none"},
    {"name": "delete", "function": "Delete_File_or_Folder", "screenshot": "none"},
    {"name": "create", "function": "Create_File_or_Folder", "screenshot": "none"},
    {"name": "find", "function": "Find_File_Or_Folder", "screenshot": "none"},
    {"name": "rename", "function": "Rename_File_or_Folder", "screenshot": "none"},
    {"name": "move", "function": "Move_File_or_Folder", "screenshot": "none"},
    {"name": "zip", "function": "Zip_File_or_Folder", "screenshot": "none"},
    {"name": "unzip", "function": "Unzip_File_or_Folder", "screenshot": "none"},
    {"name": "compare", "function": "Compare_File", "screenshot": "none"},
    {"name": "empty", "function": "Empty_Trash", "screenshot": "none"},
    {"name": "user name", "function": "Get_User_Name", "screenshot": "none"},
    {
        "name": "current documents",
        "function": "Get_Current_Documents",
        "screenshot": "none",
    },
    {
        "name": "current desktop",
        "function": "Get_Current_Desktop",
        "screenshot": "none",
    },
    {"name": "home directory", "function": "Get_Home_Directory", "screenshot": "none"},
    {"name": "run command", "function": "run_command", "screenshot": "none"},
    {"name": "download", "function": "Download_file", "screenshot": "none"},
    {"name": "log 2", "function": "Add_Log", "screenshot": "none"},
    {"name": "log 3", "function": "Add_Log", "screenshot": "none"},
    {"name": "log 1", "function": "Add_Log", "screenshot": "none"},
    {
        "name": "download and unzip",
        "function": "Download_File_and_Unzip",
        "screenshot": "none",
    },
    {"name": "take screen shot", "function": "TakeScreenShot", "screenshot": "none"},
    {"name": "change ini value", "function": "Change_Value_ini", "screenshot": "none"},
    {"name": "add ini line", "function": "Add_line_ini", "screenshot": "none"},
    {"name": "delete ini line", "function": "Delete_line_ini", "screenshot": "none"},
    {
        "name": "read name_value",
        "function": "Read_line_name_and_value",
        "screenshot": "none",
    },
    {"name": "text replace", "function": "replace_Substring", "screenshot": "none"},
    {
        "name": "count files in folder",
        "function": "count_no_of_files_in_folder",
        "screenshot": "none",
    },
    {"name": "search string", "function": "pattern_matching", "screenshot": "none"},
    {"name": "save substring", "function": "save_substring", "screenshot": "none"},
    {
        "name": "get attachment path",
        "function": "Get_Attachment_Path",
        "screenshot": "none",
    },
    {"name": "extract number", "function": "extract_number", "screenshot": "none"},
    {
        "name": "convert date format",
        "function": "convert_date_format",
        "screenshot": "none",
    },
    {"name": "compare images", "function": "compare_images", "screenshot": "none"},
    {
        "name": "datatype conversion",
        "function": "datatype_conversion",
        "screenshot": "none",
    },
)  # yapf: disable

module_name = "utility"

for dec in declarations:
    dec["module"] = module_name
