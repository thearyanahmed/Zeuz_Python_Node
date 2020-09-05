declarations = (
    {
        "screenshot": "mobile",
        "name": "click",
        "function": "Click_Element_Appium",
    },
    {
        "screenshot": "mobile",
        "name": "text",
        "function": "Enter_Text_Appium",
    },
    {
        "screenshot": "mobile",
        "name": "tap",
        "function": "Tap_Appium",
    },
    {
        "screenshot": "mobile",
        "name": "validate full text",
        "function": "Validate_Text_Appium",
    },
    {
        "screenshot": "mobile",
        "name": "validate partial text",
        "function": "Validate_Text_Appium",
    },
    {
        "screenshot": "mobile",
        "name": "install",
        "function": "install_application",
    },
    {
        "screenshot": "mobile",
        "name": "launch",
        "function": "launch_application",
    },
    {
        "screenshot": "mobile",
        "name": "get location",
        "function": "get_element_location_by_id",
    },
    {
        "screenshot": "mobile",
        "name": "swipe",
        "function": "swipe_handler_wrapper",
    },
    {
        "screenshot": "mobile",
        "name": "close",
        "function": "close_application",
    },
    {
        "screenshot": "mobile",
        "name": "uninstall",
        "function": "uninstall_application",
    },
    {
        "screenshot": "mobile",
        "name": "teardown",
        "function": "teardown_appium",
    },
    {
        "screenshot": "mobile",
        "name": "keypress",
        "function": "Keystroke_Appium",
    },
    {
        "screenshot": "mobile",
        "name": "long keypress",
        "function": "Keystroke_Appium",
    },
    {
        "screenshot": "mobile",
        "name": "reset",
        "function": "reset_application",
    },
    {
        "screenshot": "none",
        "name": "imei",
        "function": "device_information",
    },
    {
        "screenshot": "mobile",
        "name": "validate screen text",
        "function": "Validate_Text_Appium",
    },
    {
        "screenshot": "none",
        "name": "model name",
        "function": "device_information",
    },
    {
        "screenshot": "none",
        "name": "version",
        "function": "device_information",
    },
    {
        "screenshot": "none",
        "name": "serial no",
        "function": "device_information",
    },
    {
        "screenshot": "none",
        "name": "storage",
        "function": "device_information",
    },
    {
        "screenshot": "none",
        "name": "reboot",
        "function": "device_information",
    },
    {
        "screenshot": "none",
        "name": "phone name",
        "function": "device_information",
    },
    {
        "screenshot": "none",
        "name": "device password",
        "function": "set_device_password",
    },
    {
        "screenshot": "mobile",
        "name": "switch device",
        "function": "switch_device",
    },
    {
        "screenshot": "mobile",
        "name": "long press",
        "function": "Long_Press_Appium",
    },
    {
        "screenshot": "mobile",
        "name": "tap location",
        "function": "tap_location",
    },
    {
        "screenshot": "mobile",
        "name": "wake",
        "function": "device_information",
    },
    {
        "screenshot": "mobile",
        "name": "maximize",
        "function": "maximize_appilcation",
    },
    {
        "screenshot": "mobile",
        "name": "minimize",
        "function": "minimize_appilcation",
    },
    {
        "screenshot": "none",
        "name": "package version",
        "function": "package_information",
    },
    {
        "screenshot": "none",
        "name": "package installed",
        "function": "package_information",
    },
    {
        "screenshot": "mobile",
        "name": "clear and enter text",
        "function": "Clear_And_Enter_Text_Appium",
    },
    {
        "screenshot": "mobile",
        "name": "pickerwheel",
        "function": "Pickerwheel_Appium",
    },
    {
        "screenshot": "mobile",
        "name": "unlock android device",
        "function": "unlock_android_device",
    },
    {
        "screenshot": "mobile",
        "name": "unlock android app",
        "function": "unlock_android_app",
    },
    {
        "screenshot": "mobile",
        "name": "swipe in direction",
        "function": "swipe_in_direction",
    },
    {
        "screenshot": "mobile",
        "name": "if element exists",
        "function": "if_element_exists",
    },
    {
        "screenshot": "mobile",
        "name": "clear and enter text adb",
        "function": "Clear_And_Enter_Text_ADB",
    },
    {
        "screenshot": "mobile",
        "name": "hide keyboard",
        "function": "Hide_Keyboard",
    },
    {
        "screenshot": "mobile",
        "name": "handle alert",
        "function": "Handle_Mobile_Alert",
    },
    {
        "screenshot": "mobile",
        "name": "switch context",
        "function": "Switch_Context",
    },
    {
        "screenshot": "mobile",
        "name": "clear media",
        "function": "clear_existing_media_ios",
    },
    {
        "screenshot": "mobile",
        "name": "add media",
        "function": "add_media_ios",
    },
    {
        "screenshot": "mobile",
        "name": "take screenshot mobile",
        "function": "take_screenshot_appium",
    },
    {
        "screenshot": "mobile",
        "name": "save attribute",
        "function": "Save_Attribute",
    },
    {
        "screenshot": "mobile",
        "name": "go to webpage",
        "function": "go_to_webpage",
    },
)

module_name = "appium"

for dec in declarations:
    dec["module"] = module_name
