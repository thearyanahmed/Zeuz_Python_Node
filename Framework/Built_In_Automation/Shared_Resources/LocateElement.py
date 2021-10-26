# -*- coding: utf-8 -*-
# -*- coding: cp1252 -*-
"""
Created on Jun 21, 2017
@author: Built_In_Automation Solutionz Inc.
"""
import sys, time
import inspect
import traceback
from pathlib import Path
from Framework.Utilities import CommonUtil
from Framework.Utilities.CommonUtil import passed_tag_list, failed_tag_list
from Framework.Built_In_Automation.Shared_Resources import (
    BuiltInFunctionSharedResources as sr,
)
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import selenium
global WebDriver_Wait
WebDriver_Wait = 2
global generic_driver
generic_driver = None
# driver type will be set globally so we can use it anytime
global driver_type
driver_type = None


MODULE_NAME = inspect.getmodulename(__file__)


def Get_Element(step_data_set, driver, query_debug=False, wait_enable=True, return_all_elements=False):
    """
    This funciton will return "zeuz_failed" if something went wrong, else it will always return a single element
    if you are trying to produce a query from a step dataset, make sure you provide query_debug =True.  This is
    good when you are just trying to see how your step data would be converted to a query for testing local runs
    """
    try:
        sModuleInfo = inspect.currentframe().f_code.co_name + " : " + MODULE_NAME
        global generic_driver
        generic_driver = driver
        # Check the driver that is given and set the driver type
        global driver_type
        driver_type = _driver_type(query_debug)

        # Checking whether the given element is web element or web driver
        if isinstance(driver, selenium.webdriver.remote.webelement.WebElement):
            web_element_object = True
        else:
            web_element_object = False

        if driver_type == None:
            CommonUtil.ExecLog(
                sModuleInfo, "Incorrect driver. Please validate driver", 3
            )
            return "zeuz_failed"

        # We need to switch to default content just in case previous action switched to something else
        try:
            if driver_type == "selenium":
                pass #generic_driver.switch_to.default_content()
                # we need to see if there are more than one handles.  Since we cannot know if we had switch
                # windows before, we are going to assume that we can always safely switch to default handle 0
                """
                try:
                    all_windows = generic_driver.window_handles
                    generic_driver.switch_to.window(all_windows[0])
                    True
                except:
                    True
                """
            elif driver_type == "appium":

                # If we find a '|' character in the left column, then try to check the platform
                # and filter the appropriate data for the left column by removing '|'
                device_platform = (
                    generic_driver.capabilities["platformName"].strip().lower()
                )
                cleaned_data_set = []
                str_to_strip = "|*|"
                for left, middle, right in step_data_set:
                    if "element parameter" in middle:
                        # Split the attribute field if str_to_strip is present
                        if left.find(str_to_strip) != -1:
                            if device_platform == "android":
                                left = left.split(str_to_strip)[0].strip()
                            elif device_platform == "ios":
                                left = left.split(str_to_strip)[1].strip()

                        # Split the value field if str_to_strip is present
                        if right.find(str_to_strip) != -1:
                            if device_platform == "android":
                                right = right.split(str_to_strip)[0].strip()
                            elif device_platform == "ios":
                                right = right.split(str_to_strip)[1].strip()

                    new_row = (
                        left,
                        middle,
                        right,
                    )
                    cleaned_data_set.append(new_row)

                step_data_set = cleaned_data_set

                new_step_data = []
                for row in step_data_set:
                    if row[0] == "resource-id" and str(row[2]).startswith("*"):
                        new_value = row[2]
                        new_value = (
                            sr.Get_Shared_Variables("package_name")
                            + ":id/"
                            + new_value[1:]
                        )
                        new_row = [row[0], row[1], new_value]
                        new_step_data.append(new_row)
                    else:
                        new_step_data.append(row)
                step_data_set = new_step_data
        except Exception as e:
            pass  # Exceptions happen when we have an alert, but is not a problem

        save_parameter = ""
        get_parameter = ""
        Filter = ""
        for row in step_data_set:
            if row[1] == "save parameter":
                if row[2] != "ignore":
                    save_parameter = row[0]
            elif row[1].strip().lower() == "get parameter":
                if row[0].strip().startswith("%|") and row[0].strip().endswith("|%"):
                    get_parameter = row[0].strip().strip("%").strip("|")
                else:
                    CommonUtil.ExecLog(sModuleInfo, "Use '%| |%' sign to get variable value", 3)
                    return "zeuz_failed"
            elif row[1].strip().lower() == "option":
                Filter = row[0].strip().lower() if row[2].strip().lower() in ("yes", "true", "ok") else Filter

        if get_parameter != "":

            result = sr.parse_variable(get_parameter)
            result = CommonUtil.ZeuZ_map_code_decoder(result)   # Decode if this is a ZeuZ_map_code
            if result not in failed_tag_list:
                CommonUtil.ExecLog(
                    sModuleInfo,
                    "Returning saved element '%s' from shared variables"
                    % get_parameter,
                    1,
                )
                return result
            else:
                CommonUtil.ExecLog(
                    sModuleInfo,
                    "Element named '%s' not found in shared variables" % get_parameter,
                    3,
                )
                return "zeuz_failed"

        if driver_type == "pyautogui":
            result = _pyautogui(step_data_set)
            if save_parameter != "":  # save element to a variable
                sr.Set_Shared_Variables(save_parameter, result)
            return result

        # here we switch driver if we need to
        _switch(step_data_set)
        index_number = _locate_index_number(step_data_set)
        element_query, query_type = _construct_query(step_data_set, web_element_object)
        CommonUtil.ExecLog(
            sModuleInfo,
            "To locate the Element we used %s:\n%s"
            % (query_type, element_query),
            5,
        )

        if query_debug == True:
            print("This query will not be run as query_debug is enabled.  It will only print out in console")
            print("Your query from the step data provided is:  %s" % element_query)
            print("Your query type is: %s" % query_type)
            result = "passed"
        if element_query == False:
            result = "zeuz_failed"
        elif query_type == "xpath" and element_query != False:
            result = _get_xpath_or_css_element(element_query, "xpath", index_number, Filter, return_all_elements)
        elif query_type == "css" and element_query != False:
            result = _get_xpath_or_css_element(element_query, "css", index_number, Filter)
        elif query_type == "unique" and element_query != False:
            result = _get_xpath_or_css_element(element_query, "unique", index_number, Filter)
        else:
            result = "zeuz_failed"

        # if user sends optional option check if element is displayed or not. We may need to add more
        # items here such as enabled, visible and such.

        try:
            if driver_type == "appium" or driver_type == "selenium":
                is_displayed_value = ""
                for row in step_data_set:
                    if (
                        "option" in str(row[1]).lower().strip()
                        and "is_displayed" in str(row[0]).lower().strip()
                    ):
                        is_displayed_value = row[2].strip().lower()
                        if is_displayed_value == "true":
                            if not return_all_elements:
                                if not result.is_displayed():
                                    CommonUtil.ExecLog(
                                        sModuleInfo,
                                        "Element was found, however, it was not displayed or enabled. Returning failed",
                                        2,
                                    )
                                    result = "zeuz_failed"
                                    break
                                else:
                                    break
                            if return_all_elements:
                                i = 0
                                for each_element in result:
                                    i = i+1
                                    if not each_element.is_displayed():
                                        CommonUtil.ExecLog(
                                            sModuleInfo,
                                            "%s no element was not displayed or enabled. Returning failed" % i,
                                            2,
                                        )
                                        result = "zeuz_failed"
                                        break
                                break
        except:
            True

        if result not in failed_tag_list:
            if save_parameter != "":  # save element to a variable
                sr.Set_Shared_Variables(save_parameter, result)
            return result  # Return on pass
        if not wait_enable:
            CommonUtil.ExecLog(
                sModuleInfo,
                "Element not found. Waiting is disabled, so returning",
                2,
            )
            return result  # If asked not to loop, return the failure
            # If fail, but instructed to loop, do so
        return "zeuz_failed"

    except Exception:
        return CommonUtil.Exception_Handler(sys.exc_info())


def _construct_query(step_data_set, web_element_object=False):
    """
    first find out if in our dataset user is using css or xpath.  If they are using css or xpath, they cannot use any 
    other feature such as child parameter or multiple element parameter to locate the element.
    If web_element_object = True then it will generate a xpath so that find_elements can find only the child elements
    inside the given parent element
    """
    try:
        sModuleInfo = inspect.currentframe().f_code.co_name + " : " + MODULE_NAME
        collect_all_attribute = [x[0] for x in step_data_set]
        # find out if ref exists.  If it exists, it will set the value to True else False
        child_ref_exits = any("child parameter" in s for s in step_data_set)
        parent_ref_exits = any("parent parameter" in s for s in step_data_set)
        sibling_ref_exits = any("sibling parameter" in s for s in step_data_set)
        unique_ref_exists = any("unique parameter" in s for s in step_data_set)
        # get all child, element, and parent only
        child_parameter_list = [x for x in step_data_set if "child parameter" in x[1]]
        element_parameter_list = [
            x for x in step_data_set if "element parameter" in x[1]
        ]
        parent_parameter_list = [x for x in step_data_set if "parent parameter" in x[1]]
        sibling_parameter_list = [
            x for x in step_data_set if "sibling parameter" in x[1]
        ]
        unique_parameter_list = [x for x in step_data_set if "unique parameter" in x[1]]

        if (
            unique_ref_exists
            and (driver_type == "appium" or driver_type == "selenium")
            and len(unique_parameter_list) > 0
        ):  # for unique identifier
            return (
                [unique_parameter_list[0][0], unique_parameter_list[0][2]],
                "unique",
            )
        elif "css" in collect_all_attribute and "xpath" not in collect_all_attribute:
            # return the raw css command with css as type.  We do this so that even if user enters other data, we will ignore them.
            # here we expect to get raw css query
            return (([x for x in step_data_set if "css" in x[0]][0][2]), "css")
        elif "xpath" in collect_all_attribute and "css" not in collect_all_attribute:
            # return the raw xpath command with xpath as type. We do this so that even if user enters other data, we will ignore them.
            # here we expect to get raw xpath query
            return (([x for x in step_data_set if "xpath" in x[0]][0][2]), "xpath")
        elif (
            child_ref_exits == False
            and parent_ref_exits == False
            and sibling_ref_exits == False
            and web_element_object == False
        ):
            """  If  there are no child or parent as reference, then we construct the xpath differently"""
            # first we collect all rows with element parameter only
            xpath_element_list = _construct_xpath_list(element_parameter_list)
            return (_construct_xpath_string_from_list(xpath_element_list), "xpath")

        elif (
            child_ref_exits == True
            and parent_ref_exits == False
            and sibling_ref_exits == False
        ):
            """  If  There is child but making sure no parent or sibling
            //<child_tag>[child_parameter]/ancestor::<element_tag>[element_parameter]
            """
            xpath_child_list = _construct_xpath_list(child_parameter_list)
            child_xpath_string = (
                _construct_xpath_string_from_list(xpath_child_list) + "/ancestor::"
            )

            xpath_element_list = _construct_xpath_list(element_parameter_list)
            element_xpath_string = _construct_xpath_string_from_list(xpath_element_list)
            element_xpath_string = element_xpath_string.replace("//", "")

            full_query = child_xpath_string + element_xpath_string
            return (full_query, "xpath")

        elif (
            child_ref_exits == False
            and parent_ref_exits == True
            and sibling_ref_exits == False
            and (driver_type == "appium" or driver_type == "selenium")
        ):
            """  
            parent as a reference
            '//<parent tag>[<parent attributes>]/descendant::<target element tag>[<target element attribute>]'
            """
            xpath_parent_list = _construct_xpath_list(parent_parameter_list)
            parent_xpath_string = (
                _construct_xpath_string_from_list(xpath_parent_list) + "/descendant::"
            )

            xpath_element_list = _construct_xpath_list(element_parameter_list)
            element_xpath_string = _construct_xpath_string_from_list(xpath_element_list)
            element_xpath_string = element_xpath_string.replace("//", "")

            full_query = parent_xpath_string + element_xpath_string
            return (full_query, "xpath")

        elif (
            child_ref_exits == False
            and web_element_object == True
            and sibling_ref_exits == False
            and (driver_type == "appium" or driver_type == "selenium")
            and parent_ref_exits == False
        ):
            """
            'descendant::<target element tag>[<target element attribute>]'
            """
            xpath_element_list = _construct_xpath_list(element_parameter_list)
            element_xpath_string = _construct_xpath_string_from_list(xpath_element_list)
            element_xpath_string = element_xpath_string.replace("//", "")

            full_query = "descendant::" + element_xpath_string
            return (full_query, "xpath")

        elif (
            child_ref_exits == False
            and parent_ref_exits == True
            and sibling_ref_exits == True
            and (driver_type == "appium" or driver_type == "selenium")
        ):
            """  for siblings, we need parent, siblings and element.  Siblings cannot be used with just element
            xpath_format = '//<sibling_tag>[<sibling_element>]/ancestor::<immediate_parent_tag>[<immediate_parent_element>]//<target_tag>[<target_element>]'
            """
            xpath_sibling_list = _construct_xpath_list(sibling_parameter_list)
            sibling_xpath_string = (
                _construct_xpath_string_from_list(xpath_sibling_list) + "/ancestor::"
            )

            xpath_parent_list = _construct_xpath_list(parent_parameter_list)
            parent_xpath_string = _construct_xpath_string_from_list(xpath_parent_list)
            parent_xpath_string = parent_xpath_string.replace("//", "")

            xpath_element_list = _construct_xpath_list(element_parameter_list)
            element_xpath_string = _construct_xpath_string_from_list(xpath_element_list)

            full_query = (
                sibling_xpath_string + parent_xpath_string + element_xpath_string
            )
            return (full_query, "xpath")

        elif (
            child_ref_exits == False
            and parent_ref_exits == True
            and sibling_ref_exits == False
            and (driver_type == "xml")
        ):
            """  If  There is parent but making sure no child"""
            xpath_parent_list = _construct_xpath_list(parent_parameter_list)
            parent_xpath_string = _construct_xpath_string_from_list(xpath_parent_list)
            # For xml we just put parent first and element later
            xpath_element_list = _construct_xpath_list(element_parameter_list, True)
            element_xpath_string = _construct_xpath_string_from_list(xpath_element_list)
            xpath_element_list_combined = parent_xpath_string + element_xpath_string
            return (
                _construct_xpath_string_from_list(xpath_element_list_combined),
                "xpath",
            )

        elif child_ref_exits == True and (driver_type == "xml"):
            """Currently we do not support child as reference for xml"""
            CommonUtil.ExecLog(
                sModuleInfo,
                "Currently we do not support child as reference for xml.  Please contact info@automationsolutionz.com for help",
                3,
            )
            return False, False

        else:
            CommonUtil.ExecLog(
                sModuleInfo,
                "You have entered an unsupported data set.  Please contact info@automationsolutionz.com for help",
                3,
            )
            return False, False
    except Exception:
        return CommonUtil.Exception_Handler(sys.exc_info())


def _driver_type(query_debug):
    """
    This function will find out what type of driver it is.  Query changes slightly for certain cases based on appium, selenium and xml.
    """
    driver_type = None
    # check if its Appium, selenium or XML
    try:
        driver_string = str(generic_driver)
        print(driver_string)
        if query_debug == True:
            return "debug"
        elif "selenium" in driver_string or "browser" in driver_string:
            driver_type = "selenium"
        elif "appium" in driver_string:
            driver_type = "appium"
        elif "Element" in driver_string:
            driver_type = "xml"
        elif "pyautogui" in driver_string:
            driver_type = "pyautogui"
        else:
            driver_type = None
        return driver_type
    except Exception:
        return CommonUtil.Exception_Handler(sys.exc_info())


def _construct_xpath_list(parameter_list, add_dot=False):
    """
    This function constructs the raw data from step data into a xpath friendly format but in a list
    """
    try:
        # Setting the list empty
        element_main_body_list = []
        # these are special cases where we cannot treat their attribute as any other attribute such as id, class and so on...
        excluded_attribute = [
            "**text", "*text", "text",
            "tag",
            "css",
            "index",
            "xpath",
            "switch frame",
            "switch window",
            "switch alert",
            "switch active",
        ]
        for each_data_row in parameter_list:
            attribute = each_data_row[0].strip()
            attribute_value = each_data_row[2]

            if attribute == "text" and driver_type in ("selenium", "xml"):  # exact search
                text_value = '[text()="%s"]' % attribute_value
                element_main_body_list.append(text_value)
            elif attribute == "*text" and driver_type in ("selenium", "xml"):  # partial search
                text_value = '[contains(text(),"%s")]' % (str(attribute_value))
                element_main_body_list.append(text_value)
            elif attribute == "**text" and driver_type in ("selenium", "xml"):  # partial search + ignore case
                text_value = '[contains(translate(text(),"ABCDEFGHIJKLMNOPQRSTUVWXYZ","abcdefghijklmnopqrstuvwxyz"),"%s")]' % str(attribute_value).lower()
                element_main_body_list.append(text_value)

            elif attribute == "text" and driver_type == "appium":  # exact search
                current_context = generic_driver.context
                if "WEB" in current_context:
                    text_value = '[text()="%s"]' % attribute_value
                else:
                    text_value = '[@text="%s"]' % attribute_value
                element_main_body_list.append(text_value)
            elif attribute == "**text" and driver_type == "appium":  # partial search + ignore case
                text_value = "[contains(translate(@text,'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz'),'%s')]"%str(attribute_value).lower()
                current_context = generic_driver.context
                element_main_body_list.append(text_value)
            elif attribute == "*text" and driver_type == "appium":  # partial search
                current_context = generic_driver.context
                if "WEB" in current_context:
                    text_value = '[contains(%s(),"%s")]' % (attribute.split("*")[1], str(attribute_value))
                else:
                    text_value = '[contains(@%s,"%s")]' % (attribute.split("*")[1], str(attribute_value))
                element_main_body_list.append(text_value)

            elif attribute not in excluded_attribute and "*" not in attribute:  # exact search
                other_value = '[@%s="%s"]' % (attribute, attribute_value)
                element_main_body_list.append(other_value)
            elif attribute not in excluded_attribute and "**" in attribute:  # partial search + ignore case
                if driver_type == "appium":
                    other_value = "[contains(translate(@%s,'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz'),'%s')]" % (attribute.split('**')[1], str(attribute_value.lower()))
                else:
                    other_value = "[contains(translate(@%s,'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz'),'%s')]" % (attribute.split('**')[1], str(attribute_value).lower())
                element_main_body_list.append(other_value)
            elif attribute not in excluded_attribute and "*" in attribute:  # partial search
                if driver_type == "appium":
                    other_value = '[contains(@%s,"%s")]' % (attribute.split("*")[1], str(attribute_value))
                else:
                    other_value = '[contains(@%s,"%s")]' % (attribute.split("*")[1], str(attribute_value))
                element_main_body_list.append(other_value)

        # we do the tag on its own
        # tag_was_given = any("tag" in s for s in parameter_list)
        if "tag" in [x[0] for x in parameter_list]:
            tag_item = "//" + [x for x in parameter_list if "tag" in x][0][2]
        else:
            tag_item = "//*"
        if add_dot != False and driver_type != "xml":
            tag_item = "." + tag_item
        element_main_body_list.append(tag_item)
        # We need to reverse the list so that tag comes at the begining
        return list(reversed(element_main_body_list))
    except Exception:
        return CommonUtil.Exception_Handler(sys.exc_info())


def _construct_xpath_string_from_list(xpath_list):
    """
    in this function, we simply take the list and construct the actual query in string
    """
    try:
        xpath_string_format = ""
        for each in xpath_list:
            xpath_string_format = xpath_string_format + each
        return xpath_string_format
    except Exception:
        return CommonUtil.Exception_Handler(sys.exc_info())


def _switch(step_data_set):
    "here we switch the global driver to any of the switch call"
    try:
        sModuleInfo = inspect.currentframe().f_code.co_name + " : " + MODULE_NAME
        # find if frame switch is there.  If user enters more than one frame, it will ignore
        # user should enter multiple frame in this order parent > child > grand child ... and so on
        if "switch frame" in [x[0] for x in step_data_set]:
            generic_driver.switch_to.default_content()
            CommonUtil.ExecLog(
                sModuleInfo,
                "This method of 'switch frame' is deprecated and will be removed at a later period.\n" +
                "Please use our new action 'Switch iframe' to get updated features",
                2)
            frame_switch = [x for x in step_data_set if "switch frame" == x[0]][0][2]
            # first we split by > and then we reconstruct the list by striping trailing spaces
            frame_switch_list = [(x.strip()) for x in (frame_switch.split(">"))]
            # we switch each frame in order
            for each_frame in frame_switch_list:
                CommonUtil.ExecLog(sModuleInfo, "switching frame; %s" % each_frame, 1)
                # switch by index.  If index of iframe is provided, then we need to convert to int
                check_if_index = ["0", "1", "2", "3", "4", "5"]
                if each_frame in check_if_index:
                    each_frame = int(each_frame)
                if isinstance(each_frame, str) and each_frame.strip().lower() == "default content":
                    continue
                else:
                    generic_driver.switch_to_frame(each_frame)

            return True
            """
            # We are moving this as a dedicated action so that we do not need to keep switching windows for every action.
            # however, users will now need to perform switch to the main window when they are done with their actions for pop up window 
            elif "switch window" in [x[0] for x in step_data_set]: 
                #get the value of switch window
                window_switch = [x for x in step_data_set if 'switch window' == x[0]] [0][2]
                all_windows = generic_driver.window_handles
                window_handles_found = False
                for each in all_windows:
                    generic_driver.switch_to.window(each)
                    if  window_switch in (generic_driver.title):
                        window_handles_found = True
                        CommonUtil.ExecLog(sModuleInfo, "switched your window", 1)
                        break
                if window_handles_found == False:
                    CommonUtil.ExecLog(sModuleInfo, "unable to switch your window", 3)
                    return False
                else:
                    return True
            """

        elif "switch alert" in [x[0] for x in step_data_set]:
            generic_driver.switch_to_alert()
            CommonUtil.ExecLog(sModuleInfo, "switching to alert", 1)
            return True
        elif "switch active" in [x[0] for x in step_data_set]:
            CommonUtil.ExecLog(sModuleInfo, "switching to active element", 1)
            generic_driver.switch_to_active_element()
            return True
        else:
            return True
    except Exception:
        return CommonUtil.Exception_Handler(sys.exc_info())

end = 1
def _get_xpath_or_css_element(element_query, css_xpath, index_number=None, Filter="", return_all_elements=False):
    """
    Here, we actually execute the query based on css/xpath and then analyze if there are multiple.
    If we find multiple we give warning and send the first one we found.
    We also consider if user sent index. If they did, we send them the index they provided
    If return_all_elements = True then we return all elements.
    """
    try:
        all_matching_elements_visible_invisible = []
        sModuleInfo = inspect.currentframe().f_code.co_name + " : " + MODULE_NAME
        exception_msg = ""
        exception_cnd = False
        start = time.time()
        #end = start + int(sr.Get_Shared_Variables("element_wait"))
        unique_element = None
        flag=0
        displayed_len=0
        hidden_len=0
        all_matching_elements=[]
        x = 0
        #while time.time() < end:
        while x < end:
            x = x+1
            generic_driver.switch_to.default_content()
            if css_xpath == "unique" and (
                driver_type == "appium" or driver_type == "selenium"
            ):  # for unique id
                flag=1
                try:
                    unique_key = element_query[0]
                    unique_value = element_query[1]
                    if driver_type == "appium" and (
                        unique_key == "accessibility id"
                        or unique_key == "accessibility-id"
                        or unique_key == "content-desc"
                        or unique_key == "content desc"
                    ):  # content-desc for android, accessibility id for iOS
                        unique_element = generic_driver.find_element_by_accessibility_id(
                            unique_value
                        )
                    elif unique_key == "id" or (driver_type == "appium" and (unique_key == "resource id" or unique_key == "resource-id" or unique_key == "name")):  # name for iOS
                        unique_element = generic_driver.find_element(By.ID, unique_value)
                    elif unique_key == "name":
                        unique_element = generic_driver.find_element(By.NAME, unique_value)
                    elif unique_key == "class":
                        unique_element = generic_driver.find_element(
                            By.CLASS_NAME, unique_value
                        )
                    elif unique_key == "tag":
                        unique_element = generic_driver.find_element(
                            By.TAG_NAME, unique_value
                        )
                    elif unique_key == "css":
                        unique_element = generic_driver.find_element(
                            By.CSS_SELECTOR, unique_value
                        )
                    elif unique_key == "xpath":
                        unique_element = generic_driver.find_element(By.XPATH, unique_value)
                    elif unique_key in ["text", "*text"]:
                        if driver_type == "appium":
                            if unique_key == "text":
                                unique_element = generic_driver.find_element(
                                    By.XPATH, '//*[@text="%s"]' % unique_value
                                )
                            else:
                                unique_element = generic_driver.find_element(
                                    By.XPATH, '//*[contains(@text,"%s")]' % unique_value
                                )
                        else:
                            if unique_key == "text":
                                unique_element = generic_driver.find_element(
                                    By.XPATH, '//*[text()="%s"]' % unique_value
                                )
                            else:
                                unique_element = generic_driver.find_element(
                                    By.XPATH, '//*[contains(text(),"%s")]' % unique_value
                                )
                    else:
                        if "*" in unique_key:
                            unique_key = unique_key[1:]  # drop the asterisk
                            unique_element = generic_driver.find_element(
                                By.XPATH,
                                "//*[contains(@%s,'%s')]" % (unique_key, unique_value),
                            )
                        else:
                            unique_element = generic_driver.find_element(
                                By.XPATH, "//*[@%s='%s']" % (unique_key, unique_value)
                            )
                    if unique_element != None:
                        return unique_element
                except :
                    #exception_msg = e
                    exception_cnd = True
                    continue
            elif css_xpath == "xpath" and driver_type != "xml":
                all_matching_elements_visible_invisible = generic_driver.find_elements(By.XPATH, element_query)
                all_matching_elements = filter_elements(all_matching_elements_visible_invisible, Filter)
                if Filter == "allow hidden":
                    displayed_len += len(filter_elements(all_matching_elements_visible_invisible, ""))
                    hidden_len = len(all_matching_elements_visible_invisible) - displayed_len
                else:
                    displayed_len += len(all_matching_elements)
                    hidden_len = len(all_matching_elements_visible_invisible) - displayed_len

            elif css_xpath == "xpath" and driver_type == "xml":
                all_matching_elements_visible_invisible = generic_driver.xpath(element_query)
                all_matching_elements = filter_elements(all_matching_elements_visible_invisible, Filter)
                if Filter == "allow hidden":
                    displayed_len += len(filter_elements(all_matching_elements_visible_invisible, ""))
                    hidden_len = len(all_matching_elements_visible_invisible) - displayed_len
                else:
                    displayed_len += len(all_matching_elements)
                    hidden_len = len(all_matching_elements_visible_invisible) - displayed_len

            elif css_xpath == "css":
                all_matching_elements_visible_invisible = generic_driver.find_elements(By.CSS_SELECTOR, element_query)
                all_matching_elements = filter_elements(all_matching_elements_visible_invisible, Filter)
                if Filter == "allow hidden":
                    displayed_len += len(filter_elements(all_matching_elements_visible_invisible, ""))
                    hidden_len = len(all_matching_elements_visible_invisible) - displayed_len
                else:
                    displayed_len += len(all_matching_elements)
                    hidden_len = len(all_matching_elements_visible_invisible) - displayed_len

            if len(all_matching_elements_visible_invisible) > 0 and len(filter_elements(all_matching_elements_visible_invisible, "")) > 0:
                break
            time.sleep(1)
        # end of while loop

        i = 0 if index_number is None else index_number
        if exception_cnd  or len(all_matching_elements_visible_invisible) <= i:
            generic_driver.switch_to.default_content()
            iframes = generic_driver.find_elements_by_tag_name('iframe') #find all the iframes in the default frame
            all_matching_elements_visible_invisible,unique_element, all_matching_elements,displayed_len, hidden_len = auto_frame_switch(len(iframes), [],unique_element,element_query,css_xpath, i, Filter,[],displayed_len,hidden_len )

        #flag ==1 means function returned the unique element
        if flag == 1:
            return unique_element


        tot_len = len(all_matching_elements_visible_invisible)
        if (Filter == "allow hidden" and (index_number is None and tot_len == 0) or (index_number is not None and tot_len <= index_number))\
        or ((index_number is None and displayed_len == 0) or (index_number is not None and displayed_len <= index_number)):
            pass

        if return_all_elements:
            if Filter == "allow hidden":
                CommonUtil.ExecLog(
                    "",
                    "Found %s hidden elements and %s displayed elements. Returning all of them"
                    % (hidden_len, displayed_len),
                    1
                )
            else:
                CommonUtil.ExecLog(
                    "",
                    "Found %s hidden elements and %s displayed elements. Returning %s displayed elements only"
                    % (hidden_len, displayed_len, displayed_len),
                    1
                )
            return all_matching_elements
        elif len(all_matching_elements) == 0:
            if hidden_len > 0 and Filter != "allow hidden":
                CommonUtil.ExecLog(
                    "",
                    "Found %s hidden elements and no displayed elements. Nothing to return.\n" % hidden_len +
                    "To get hidden elements add a row (\"allow hidden\", \"optional option\", \"yes\")",
                    3
                )
            return False
        elif len(all_matching_elements) == 1 and index_number is None:
            if hidden_len > 0 and Filter != "allow hidden":
                CommonUtil.ExecLog(
                    "",
                    "Found %s hidden elements and %s displayed elements. Returning the displayed element only\n" % (hidden_len, displayed_len) +
                    "To get hidden elements add a row (\"allow hidden\", \"optional option\", \"yes\") and also consider providing index",
                    2
                )
            elif Filter == "allow hidden":
                CommonUtil.ExecLog("", "Found %s hidden element and %s displayed element" % (hidden_len, displayed_len), 1)
            return all_matching_elements[0]
        elif len(all_matching_elements) > 1 and index_number is None:
            if hidden_len > 0 and Filter != "allow hidden":
                CommonUtil.ExecLog(
                    "",
                    "Found %s hidden elements and %s displayed elements. Returning the first displayed element only\n" % (hidden_len, displayed_len) +
                    "To get hidden elements add a row (\"allow hidden\", \"optional option\", \"yes\") and also consider providing index",
                    2
                )
            elif Filter != "allow hidden":
                CommonUtil.ExecLog(
                    "",
                    "Found %s displayed elements. Returning the first displayed element only. Consider providing index" % displayed_len,
                    2
                )
            else:
                CommonUtil.ExecLog(
                    "",
                    "Found %s hidden elements and %s displayed elements. Returning the first element only. Consider providing index" % (hidden_len, displayed_len),
                    2
                )
            return all_matching_elements[0]
        elif len(all_matching_elements) == 1 and index_number not in (-1, 0):
            if hidden_len > 0 and Filter != "allow hidden":
                CommonUtil.ExecLog(
                    sModuleInfo,
                    "Found %s hidden elements and %s displayed elements but you provided a wrong index number. Returning the only displayed element\n" % (hidden_len, displayed_len) +
                    "To get hidden elements add a row (\"allow hidden\", \"optional option\", \"yes\") and also consider providing correct index",
                    2,
                )
            elif Filter != "allow hidden":
                CommonUtil.ExecLog(
                    sModuleInfo,
                    "Found 0 hidden elements and %s displayed elements but you provided a wrong index number. Returning the only displayed element\n" % displayed_len,
                    2,
                )
            elif Filter == "allow hidden":
                CommonUtil.ExecLog(
                    "",
                    "Found %s hidden element and %s displayed element but you provided a wrong index number. Returning the only element" % (hidden_len, displayed_len),
                    2
                )
            return all_matching_elements[0]
        elif len(all_matching_elements) == 1 and index_number in (-1, 0):
            if hidden_len > 0 and Filter != "allow hidden":
                CommonUtil.ExecLog(
                    "",
                    "Found %s hidden elements and %s displayed elements. Returning the displayed element of index %s\n" % (hidden_len, displayed_len, index_number) +
                    "To get hidden elements add a row (\"allow hidden\", \"optional option\", \"yes\")",
                    1
                )
            elif Filter != "allow hidden":
                CommonUtil.ExecLog(
                    "",
                    "Found 0 hidden elements and %s displayed elements. Returning the displayed element of index %s" % (displayed_len, index_number),
                    1
                )
            elif Filter == "allow hidden":
                CommonUtil.ExecLog(
                    "",
                    "Found %s hidden elements and %s displayed elements. Returning the element of index %s" % (hidden_len, displayed_len, index_number),
                    1
                )
            return all_matching_elements[0]
        elif len(all_matching_elements) > 1 and index_number is not None:
            # if (len(all_matching_elements) - 1) < abs(index_number):
            if -len(all_matching_elements) <= index_number < len(all_matching_elements):
                if hidden_len > 0 and Filter != "allow hidden":
                    CommonUtil.ExecLog(
                        "",
                        "Found %s hidden elements and %s displayed elements. Returning the displayed element of index %s\n" % (hidden_len, displayed_len, index_number) +
                        "To get hidden elements add a row (\"allow hidden\", \"optional option\", \"yes\")",
                        1
                    )
                elif Filter != "allow hidden":
                    CommonUtil.ExecLog(
                        "",
                        "Found 0 hidden elements and %s displayed elements. Returning the displayed element of index %s" % (displayed_len, index_number),
                        1
                    )
                else:
                    CommonUtil.ExecLog(
                        "",
                        "Found %s hidden elements and %s displayed elements. Returning the element of index %s" % (hidden_len, displayed_len, index_number),
                        1
                    )
                return all_matching_elements[index_number]
            else:
                if hidden_len > 0 and Filter != "allow hidden":
                    CommonUtil.ExecLog(
                        "",
                        "Found %s hidden elements and %s displayed elements. Index exceeds the number of displayed elements found\n" % (hidden_len, displayed_len) +
                        "To get hidden elements add a row (\"allow hidden\", \"optional option\", \"yes\") and also consider providing correct index",
                        3
                    )
                elif Filter != "allow hidden":
                    CommonUtil.ExecLog(
                        "",
                        "Found 0 hidden elements and %s displayed elements. Index exceeds the number of displayed elements found" % displayed_len,
                        3
                    )
                else:
                    CommonUtil.ExecLog(
                        "",
                        "Found %s hidden elements and %s displayed elements. Index exceeds the number of elements found" % (hidden_len, displayed_len),
                        3
                    )
                return "zeuz_failed"
        else:
            return "zeuz_failed"
    except Exception:
        return CommonUtil.Exception_Handler(sys.exc_info())
        # Don't want to show error messages from here, especially for wait_for_element()
        # CommonUtil.ExecLog(sModuleInfo, "Exception caught - %s" % str(sys.exc_info()), 0)
        # return "zeuz_failed"


def filter_elements(all_matching_elements_visible_invisible, Filter):
    # visible, enable
    all_matching_elements = []
    try:
        if Filter != "allow hidden":
            for each in all_matching_elements_visible_invisible:
                try:
                    if each.is_displayed():
                        all_matching_elements.append(each)
                except:
                    pass
            return all_matching_elements
        else:
            return all_matching_elements_visible_invisible
    except:
        all_matching_elements = []
        return all_matching_elements


def _locate_index_number(step_data_set):
    """
    Check if index exists, if it does, get the index value.
    if we cannot convert index to integer, set it to None
    """
    try:
        if "index" in [x[0] for x in step_data_set]:
            index_number = [x for x in step_data_set if "index" in x[0]][0][2]
            try:
                index_number = int(index_number)
            except:
                index_number = None
        else:
            index_number = None
        return index_number
    except Exception:
        return CommonUtil.Exception_Handler(sys.exc_info())


def _pyautogui(step_data_set):
    """ Gets coordinates for pyautogui (doesn't provide an object) """

    """ 
    Valid files:
        We do our best to find the file for the user, it can be:
            Full path. Eg: /home/user/test.png
            Local directory. Eg: test.png
            Zeuz File Attachment. Eg: test.png - The full path is in the Shared Variables under the filename

    If provided, scales image to fit currently displayed resolution, so as to provide a more accurate match 
        There are three modes of operation:
            No resolution - don't re-scale: (image, element paramater, filename.png)
            Resolution in filename - scale accordingly: (image, element paramater, filename-1920x1080.png)
            Resolution in step data - scale accordingly: (1920x1080, element paramater, filename.png)
            
    If a reference element is provided (parent/child parameter, name doens't matter), then we have three methods by which to locate the element of interest:
        Field = left, right, up, down - we'll favour any elements in this direction and return it
        Field = INDEX NUMBER - If a number is provided (>=1), we'll return the nTH element found
        Field = ANYTHING ELSE - We'll find the closest element to it
    """

    # Only used by desktop, so only import here
    import pyautogui, os.path, re

    sModuleInfo = inspect.currentframe().f_code.co_name + " : " + MODULE_NAME

    # Recall file attachment, if not already set
    file_attachment = []
    if sr.Test_Shared_Variables("file_attachment"):
        file_attachment = sr.Get_Shared_Variables("file_attachment")

    # Parse data set
    try:
        file_name = ""
        file_name_parent = ""
        resolution = ""
        direction = "all"
        index = False
        for row in step_data_set:
            if row[1] == "element parameter":  # Find element line
                file_name = row[2]  # Save Value as the filename
                resolution = row[0]  # Save the resolution of the source of the image, if provided
            if row[1] in ("child parameter", "parent parameter"):  # Find a related image, that we'll use as a reference point
                file_name_parent = row[2]  # Save Value as the filename
                direction = row[0].lower().strip()  # Save Field as a possible distance or index
            elif row[1] == "action" and file_name == "":  # Alternative method, there is no element parameter, so filename is expected on the action line
                file_name = Path(row[2])  # Save Value as the filename

        # Check that we have some value
        if file_name == "":
            return "zeuz_failed"

        # Try to find the image file
        if file_name not in file_attachment and not os.path.exists(file_name):
            CommonUtil.ExecLog(
                sModuleInfo,
                "Could not find file attachment called %s, and could not find it locally" % file_name,
                3,
            )
            return "zeuz_failed"
        if file_name in file_attachment:
            file_name = file_attachment[file_name]  # In file is an attachment, get the full path

        if file_name_parent != "":
            if file_name_parent not in file_attachment and not os.path.exists(file_name_parent):
                CommonUtil.ExecLog(
                    sModuleInfo,
                    "Could not find file attachment called %s, and could not find it locally" % file_name_parent,
                    3,
                )
                return "zeuz_failed"
            if file_name_parent in file_attachment:
                file_name_parent = file_attachment[file_name_parent]  # In file is an attachment, get the full path

        # Now file_name should have a directory/file pointing to the correct image

        # There's a problem when running from Zeuz with encoding. pyautogui seems sensitive to it. This fixes that
        # file_name = file_name.encode('ascii')
        if file_name_parent != "":
            file_name_parent = file_name_parent.encode("ascii")

    except:
        return CommonUtil.Exception_Handler(sys.exc_info(), None, "Error parsing data set")

    # Parse direction (physical direction, index or nothing)
    if direction != "all":  # If a reference image was specified (direction would be set to a different value)
        try:
            if direction in ("left", "right", "up", "down"):  # User specified a direction to look for the element
                pass
            else:
                try:
                    direction = int(direction)  # Test if it's a number, if so, format it properly
                    index = True
                    direction -= 1  #  Offset by one, because user will set first element as one, but in the array it's element zero
                except:  # Not a number
                    direction = "all"  # Default to search all directions equally (find the closest image alement to the reference)
        except:
            return CommonUtil.Exception_Handler(sys.exc_info(), None, "Error parsing direction")

    # Find element information
    try:
        # Scale image if required
        regex = re.compile(r"(\d+)\s*x\s*(\d+)", re.IGNORECASE)  # Create regex object with expression
        match = regex.search(file_name)  # Search for resolution within filename (this is the resolution of the screen the image was captured on)
        if match is None and resolution != "":  # If resolution not in filename, try to find it in the step data
            match = regex.search(resolution)  # Search for resolution within the Field of the element paramter row (this is the resolution of the screen the image was captured on)

        if match is not None:  # Match found, so scale
            CommonUtil.ExecLog(sModuleInfo, "Scaling image (%s)" % match.group(0), 0)
            size_w, size_h = (
                int(match.group(1)),
                int(match.group(2)),
            )  # Extract width, height from match (is screen resolution of desktop image was taken on)
            file_name = _scale_image(file_name, size_w, size_h)  # Scale image element
            if file_name_parent != "":
                file_name_parent = _scale_image(file_name_parent, size_w, size_h)  # Scale parent image element

        # Find image on screen (file_name here is either an actual directory/file or a PIL image object after scaling)
        start = time.time()
        while time.time() < start + int(sr.Get_Shared_Variables("element_wait")):
            element = pyautogui.locateAllOnScreen(
                file_name, grayscale=True, confidence=0.85
            )  # Get coordinates of element. Use greyscale for increased speed and better matching across machines. May cause higher number of false-positives
            element_list = tuple(element)
            if element_list:
                break
            time.sleep(0.1)
        #         if len(tuple(tmp)) == 0: # !!! This should work, but accessing the generator causes it to lose one or more of it's results, thus causing an error when we  try to use it with a single image
        #             print ">>>>IN", element
        #             CommonUtil.ExecLog(sModuleInfo, "Image element not found", 0)
        #             return "zeuz_failed"

        ################################################################################
        ######################### ALL PIECES SET - FIND ELEMENT ########################
        ################################################################################

        # If no reference image, just return the first match
        if file_name_parent == "":
            # element_list = tuple(element)
            # First match reassigned as the only element
            element = element_list[0] if len(element_list) > 0 else None

        # Reference image specified, so find the closest image element to it
        else:
            CommonUtil.ExecLog(sModuleInfo, "Locating with a reference element", 0)

            # Get coordinates of reference image
            start = time.time()
            while time.time() < start + int(sr.Get_Shared_Variables("element_wait")):
                element_parent = pyautogui.locateOnScreen(
                    file_name_parent, grayscale=True, confidence=0.85
                )
                if element_parent:
                    break
                time.sleep(0.1)
            if element_parent == None:
                CommonUtil.ExecLog(sModuleInfo, "Reference image not found", 0)
                return "zeuz_failed"

            # Initialize variables
            parent_centre = (
                element_parent[0] + int(element_parent[2] / 2),
                element_parent[1] + int(element_parent[3] / 2),
            )  # Calculate centre coordinates of parent
            element_result = (
                []
            )  # This will hold the best match that we've found as we check them all
            distance_new = [0, 0]  # This will hold the current distance
            distance_best = [0, 0]  # This will hold the distance for the best match

            # User provided an index number, so find the nTH element
            if index == True:
                try:
                    element = tuple(element)[direction]
                except:
                    return CommonUtil.Exception_Handler(sys.exc_info(), None, "Provided index number is invalid")

            # User provided a direction, or no indication, so try to find the element based on that
            else:
                # Loop through all found elements, and find the one that is closest to the reference image element
                for e in element:
                    # Calculate centre of image to centre of reference image
                    distance_new[0] = parent_centre[0] - (e[0] + int(e[2] / 2))
                    distance_new[1] = parent_centre[1] - (e[1] + int(e[3] / 2))

                    # Remove negavite values, depending on direction. This allows us to favour a certain direction by keeping the original number
                    if direction == "all":
                        distance_new[0] = abs(distance_new[0])  # Remove negative sign for x
                        distance_new[1] = abs(distance_new[1])  # Remove negative sign for y
                    elif direction in ("up", "down"):
                        distance_new[0] = abs(distance_new[0])  # Remove negative sign for x - we don't care about that direction
                    elif direction in ("left", "right"):
                        distance_new[1] = abs(distance_new[1])  # Remove negative sign for y - we don't care about that direction

                    # Compare distances
                    if element_result == []:  # First run, just save this as the closest match
                        element_result = e
                        distance_best = list(distance_new)  # Very important! - this must be saved with the list(), because python will make distance_best a pointer to distance_new without it, thus screwing up what we are trying to do. Thanks Python.
                    else:  # Subsequent runs, compare distances
                        if direction == "all" and (distance_new[0] < distance_best[0] or distance_new[1] < distance_best[1]):  # If horozontal or vertical is closer than our best/closest distance that we've found thus far
                            element_result = e  # Save this element as the best match
                            distance_best = list(distance_new)  # Save the distance for further comparison
                        elif direction == "up" and (distance_new[0] < distance_best[0] or distance_new[1] > distance_best[1]):  # Favour Y direction up
                            element_result = e  # Save this element as the best match
                            distance_best = list(
                                distance_new
                            )  # Save the distance for further comparison
                        elif direction == "down" and (distance_new[0] < distance_best[0] or distance_new[1] < distance_best[1]):  # Favour Y direction down
                            element_result = e  # Save this element as the best match
                            distance_best = list(distance_new)  # Save the distance for further comparison
                        elif direction == "left" and (distance_new[0] > distance_best[0] or distance_new[1] < distance_best[1]):  # Favour X direction left
                            element_result = e  # Save this element as the best match
                            distance_best = list(distance_new)  # Save the distance for further comparison
                        elif direction == "right" and (distance_new[0] < distance_best[0] or distance_new[1] < distance_best[1]):  # Favour X direction right
                            element_result = e  # Save this element as the best match
                            distance_best = list(distance_new)  # Save the distance for further comparison

                # Whether there is one or more matches, we now have the closest image to our reference, so save the result in the common variable
                element = element_result

        # Check result
        if element is None or element in failed_tag_list or element == "":
            return "zeuz_failed"
        else:
            return element

    except:
        traceback.print_exc()
        return "zeuz_failed"


def _scale_image(file_name, size_w, size_h):
    """ This function calculates ratio and scales an image for comparison by _pyautogui() """

    sModuleInfo = inspect.currentframe().f_code.co_name + " : " + MODULE_NAME

    # Only used by desktop, so only import here
    import pyautogui
    from PIL import Image
    from decimal import Decimal

    try:
        # Open image file
        file_name = open(file_name, "rb")  # Read file into memory
        file_name = Image.open(file_name)  # Convert to PIL format

        # Read sizes
        screen_w, screen_h = pyautogui.size()  # Read screen resolution
        image_w, image_h = file_name.size  # Read the image element's actual size

        # Calculate new image size
        if size_w > screen_w:  # Make sure we create the scaling ratio in the proper direction
            ratio = Decimal(size_w) / Decimal(screen_w)  # Get ratio (assume same for height)
        else:
            ratio = Decimal(screen_w) / Decimal(size_w)  # Get ratio (assume same for height)
        size = (int(image_w * ratio), int(image_h * ratio))  # Calculate new resolution of image element

        # Scale image
        file_name.thumbnail(size, Image.ANTIALIAS)  # Resize image per calculation above

        return file_name  # Return the scaled image object
    except:
        return CommonUtil.Exception_Handler(sys.exc_info(), None, "Error scaling image")


def auto_frame_switch(number_of_iframes,all_matching_elements_visible_invisible,unique_element,element_query,css_xpath, element_index, Filter,all_matching_elements,displayed_len,hidden_len ):
    try:
        for idx in range(number_of_iframes):
            generic_driver.switch_to.frame(idx)

            if css_xpath == "unique" and (
                driver_type == "appium" or driver_type == "selenium"
            ):  # for unique id
                try:
                    unique_key = element_query[0]
                    unique_value = element_query[1]
                    if driver_type == "appium" and (
                        unique_key == "accessibility id"
                        or unique_key == "accessibility-id"
                        or unique_key == "content-desc"
                        or unique_key == "content desc"
                    ):  # content-desc for android, accessibility id for iOS
                        unique_element = generic_driver.find_element_by_accessibility_id(
                            unique_value
                        )
                    elif unique_key == "id" or (driver_type == "appium" and (unique_key == "resource id" or unique_key == "resource-id" or unique_key == "name")):  # name for iOS
                        unique_element = generic_driver.find_element(By.ID, unique_value)
                    elif unique_key == "name":
                        unique_element = generic_driver.find_element(By.NAME, unique_value)
                    elif unique_key == "class":
                        unique_element = generic_driver.find_element(
                            By.CLASS_NAME, unique_value
                        )
                    elif unique_key == "tag":
                        unique_element = generic_driver.find_element(
                            By.TAG_NAME, unique_value
                        )
                    elif unique_key == "css":
                        unique_element = generic_driver.find_element(
                            By.CSS_SELECTOR, unique_value
                        )
                    elif unique_key == "xpath":
                        unique_element = generic_driver.find_element(By.XPATH, unique_value)
                    elif unique_key in ["text", "*text"]:
                        if driver_type == "appium":
                            if unique_key == "text":
                                unique_element = generic_driver.find_element(
                                    By.XPATH, '//*[@text="%s"]' % unique_value
                                )
                            else:
                                unique_element = generic_driver.find_element(
                                    By.XPATH, '//*[contains(@text,"%s")]' % unique_value
                                )
                        else:
                            if unique_key == "text":
                                unique_element = generic_driver.find_element(
                                    By.XPATH, '//*[text()="%s"]' % unique_value
                                )
                            else:
                                unique_element = generic_driver.find_element(
                                    By.XPATH, '//*[contains(text(),"%s")]' % unique_value
                                )
                    else:
                        if "*" in unique_key:
                            unique_key = unique_key[1:]  # drop the asterisk
                            unique_element = generic_driver.find_element(
                                By.XPATH,
                                "//*[contains(@%s,'%s')]" % (unique_key, unique_value),
                            )
                        else:
                            unique_element = generic_driver.find_element(
                                By.XPATH, "//*[@%s='%s']" % (unique_key, unique_value)
                            )
                    if unique_element != None:
                        return all_matching_elements_visible_invisible,unique_element,all_matching_elements, displayed_len, hidden_len
                except:
                    pass

            elif css_xpath == "xpath" and driver_type != "xml":
                all_matching_elements_visible_invisible += generic_driver.find_elements(By.XPATH, element_query)
                all_matching_elements = filter_elements(all_matching_elements_visible_invisible, Filter)
                if Filter == "allow hidden":
                    displayed_len += len(filter_elements(all_matching_elements_visible_invisible, ""))
                    hidden_len = len(all_matching_elements_visible_invisible) - displayed_len
                else:
                    displayed_len += len(all_matching_elements)
                    hidden_len = len(all_matching_elements_visible_invisible) - displayed_len

            elif css_xpath == "xpath" and driver_type == "xml":
                all_matching_elements_visible_invisible += generic_driver.xpath(element_query)
                all_matching_elements = filter_elements(all_matching_elements_visible_invisible, Filter)
                if Filter == "allow hidden":
                    displayed_len += len(filter_elements(all_matching_elements_visible_invisible, ""))
                    hidden_len = len(all_matching_elements_visible_invisible) - displayed_len
                else:
                    displayed_len += len(all_matching_elements)
                    hidden_len = len(all_matching_elements_visible_invisible) - displayed_len

            elif css_xpath == "css":
                all_matching_elements_visible_invisible += generic_driver.find_elements(By.CSS_SELECTOR, element_query)
                all_matching_elements = filter_elements(all_matching_elements_visible_invisible, Filter)
                if Filter == "allow hidden":
                    displayed_len += len(filter_elements(all_matching_elements_visible_invisible, ""))
                    hidden_len = len(all_matching_elements_visible_invisible) - displayed_len
                else:
                    displayed_len += len(all_matching_elements)
                    hidden_len = len(all_matching_elements_visible_invisible) - displayed_len


            if len(all_matching_elements_visible_invisible) > element_index:
                return all_matching_elements_visible_invisible,unique_element,all_matching_elements, displayed_len, hidden_len

            iframes = generic_driver.find_elements_by_tag_name('iframe')
            # if there is nested iframes it will call the function recursively
            if len(iframes) != 0:
                all_matching_elements_visible_invisible,unique_element,all_matching_elements, displayed_len, hidden_len = auto_frame_switch(len(iframes), all_matching_elements_visible_invisible, unique_element, element_query, css_xpath, element_index, Filter,all_matching_elements,displayed_len,hidden_len )
                if len(all_matching_elements_visible_invisible) > element_index:
                    return all_matching_elements_visible_invisible,unique_element, all_matching_elements, displayed_len, hidden_len

                generic_driver.switch_to.parent_frame()
            else:
                generic_driver.switch_to.parent_frame()

        return all_matching_elements_visible_invisible, unique_element, all_matching_elements, displayed_len, hidden_len

    except:
        generic_driver.switch_to.default_content()
        return CommonUtil.Exception_Handler(sys.exc_info(), None, "Exception Occured during auto iframe switch")

"""
#Sample sibling Example1:
#xpath_format = '//<sibling_tag>[<sibling_element>]/ancestor::<immediate_parent_tag>[<immediate_parent_element>]//<target_tag>[<target_element>]'

#step_data_set =  [( 'tag' , 'parent parameter' , 'tagvale' , False , False ) , ( 'id' , 'element parameter' , 'twotabsearchtextbox' , False , False ) , ( 'text' , 'selenium action' , 'Camera' , False , False ), ( 'class' , 'sibling parameter' , 'twotabsearchtextbox' , False , False ), ( 'class' , 'parent parameter' , 'twotabsearchtextbox' , False , False )]

#step_data_set = [ ( 'role' , 'element parameter' , 'checkbox' , False , False , '' ) , ( 'text' , 'sibling parameter' , 'charlie' , False , False , '' ) , ( '*class' , 'parent parameter' , 'md-table-row' , False , False , '' ) , ( 'click' , 'selenium action' , 'click' , False , False , '' ) ] 



#Sample parent and element:
#'//*[@bblocalname="deviceActivationPasswordTextBox"]/descendant::*[@type="password"]'
#step_data_set = [ ( 'typ' , 'element parameter' , 'password' , False , False , '' ) , ( 'text' , 'selenium action' , 'your password' , False , False , '' ) , ( 'bblocalname' , 'parent parameter' , 'deviceActivationPasswordTextBox' , False , False , '' ) ] 



step_data_set = [ ( '*resource-id' , 'element parameter' , 'com.assetscience.androidprodiagnostics.cellmd:id/next' , False , False ) , ( 'click' , 'appium action' , 'na' , False , False ) ]


driver = None
query_debug = True
global driver_type 
driver_type = "selenium"
global debug 
debug = True
print _construct_query (step_data_set)"""
