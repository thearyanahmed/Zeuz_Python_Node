
# Android environment
from appium import webdriver
import os , sys, time, inspect, json
from Utilities import CommonUtil, FileUtilities
from Built_In_Automation.Mobile.Android.adb_calls import adbOptions
from appium.webdriver.common.touch_action import TouchAction


PATH = lambda p: os.path.abspath(
    os.path.join(os.path.dirname(__file__), p)
)


#if local_run is True, no logging will be recorded to the web server.  Only local print will be displayed
#local_run = True
local_run = False

global APPIUM_DRIVER_LIST
APPIUM_DRIVER_LIST = {}


def getDriversList():
    return APPIUM_DRIVER_LIST


def getDriver(index):
    try:
        return APPIUM_DRIVER_LIST[index]
    except Exception, e:
        return False


def addDriver(position, driver, port):
    try:
        APPIUM_DRIVER_LIST.update({position: {'driver':driver, 'port': port}})
        return True
    except Exception, e:
        return False


def start_selenium_hub(file_location = os.path.join(FileUtilities.get_home_folder(), os.path.join('Desktop', 'selenium-server-standalone-2.43.1.jar'))):
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    try:
        CommonUtil.ExecLog(sModuleInfo, "Starting Selenium Hub", 1, local_run)
        console_run("java -jar %s -role hub" % file_location)
        CommonUtil.ExecLog(sModuleInfo, "Selenium Hub Command given", 1, local_run)
        return True
    except Exception, e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        Error_Detail = ((str(exc_type).replace("type ", "Error Type: ")) + ";" + "Error Message: " + str(
            exc_obj) + ";" + "File Name: " + fname + ";" + "Line: " + str(exc_tb.tb_lineno))
        CommonUtil.ExecLog(sModuleInfo, "Unable to Start Selenium Hub: Error:%s" % (Error_Detail), 3, local_run)
        return False

def console_run(run_command):
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    try:
        os.system("gnome-terminal --working-directory %s -e 'bash -c \"%s ;exec bash\"'" % (FileUtilities.get_home_folder(),run_command))
    except Exception, e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        Error_Detail = ((str(exc_type).replace("type ", "Error Type: ")) + ";" + "Error Message: " + str(
            exc_obj) + ";" + "File Name: " + fname + ";" + "Line: " + str(exc_tb.tb_lineno))
        CommonUtil.ExecLog(sModuleInfo, "Unable to run command", 3, local_run)
        return False


def init_config_for_device(port_to_connect, device_index, hub_address='127.0.0.1', hub_port=4444, base_location = os.path.join(FileUtilities.get_home_folder(), os.path.join('Desktop', 'appiumConfig')), **kwargs):
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    try:
        dictJson={
            "configuration":
                {
                    "nodeTimeout": 120,
                    "port": port_to_connect,
                    "hubPort": hub_port,
                    "proxy": "org.openqa.grid.selenium.proxy.DefaultRemoteProxy",
                    "url": "http://%s:%d/wd/hub"%(hub_address,port_to_connect),
                    "hub": "%s:%d/grid/register"%(hub_address, hub_port),
                    "hubHost": "%s"%(hub_address),
                    "nodePolling": 2000,
                    "registerCycle": 10000,
                    "register": True,
                    "cleanUpCycle": 2000,
                    "timeout": 30000,
                    "maxSession": 1
                }
        }
        dictJson.update({'capabilities':[kwargs]})
        if not os.path.exists(base_location):
            FileUtilities.CreateFolder(base_location)
        file_location = os.path.join(base_location, 'nodeConfig%d.json'%device_index)
        with open(file_location, 'w') as txtfile:
            json.dump(dictJson, txtfile)
        #start appium instance
        set_appium_specific_variable()
        start_appium_instances(port_to_connect, file_location)
        return True
    except Exception, e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        Error_Detail = ((str(exc_type).replace("type ", "Error Type: ")) + ";" + "Error Message: " + str(
            exc_obj) + ";" + "File Name: " + fname + ";" + "Line: " + str(exc_tb.tb_lineno))
        CommonUtil.ExecLog(sModuleInfo, "Unable to initiate appium instance for device:%d"%device_index, 3, local_run)
        return False


def set_appium_specific_variable():
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    try:
        env_vars = {'PATH': '', 'LD_LIBRARY_PATH': '', 'ANDROID_HOME': '', 'HOME': ''}
        not_set = False

        for var in env_vars.keys():
            env_value = os.getenv(var)

            if env_value:
                env_vars[var] = env_value

            elif not env_value:
                not_set = True

        if not_set:
            os.environ['PATH'] = env_vars['HOME'] + "/.linuxbrew/bin:" + env_vars['PATH']
            env_vars['PATH'] = env_vars['HOME'] + "/.linuxbrew/bin:" + env_vars['PATH']

            os.environ['LD_LIBRARY_PATH'] = env_vars['HOME'] + "/.linuxbrew/lib:" + env_vars['LD_LIBRARY_PATH']
            env_vars['LD_LIBRARY_PATH'] = env_vars['HOME'] + "/.linuxbrew/lib:" + env_vars['LD_LIBRARY_PATH']

            os.environ['ANDROID_HOME'] = os.path.join(FileUtilities.get_home_folder(), "android-sdk-linux")
            env_vars['ANDROID_HOME'] = os.path.join(FileUtilities.get_home_folder(), "android-sdk-linux")

            os.environ['PATH'] = env_vars['PATH'] + ":" + env_vars['ANDROID_HOME'] + "/tools:" + \
                                 env_vars['ANDROID_HOME'] + "/platform-tools"
            env_vars['PATH'] = env_vars['PATH'] + ":" + env_vars['ANDROID_HOME'] + "/tools:" + \
                               env_vars['ANDROID_HOME'] + "/platform-tools"
    except Exception, e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        Error_Detail = ((str(exc_type).replace("type ", "Error Type: ")) + ";" + "Error Message: " + str(
            exc_obj) + ";" + "File Name: " + fname + ";" + "Line: " + str(exc_tb.tb_lineno))
        CommonUtil.ExecLog(sModuleInfo, "Unable to set appium variable", 3, local_run)
        return False

def start_appium_instances(port_to_connect, file_location, hub_address = '127.0.0.1' ):
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    try:
        run_command = "appium -a %s -p %d --nodeconfig %s" % (hub_address, port_to_connect, file_location)
        console_run(run_command)
    except Exception, e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        Error_Detail = ((str(exc_type).replace("type ", "Error Type: ")) + ";" + "Error Message: " + str(
            exc_obj) + ";" + "File Name: " + fname + ";" + "Line: " + str(exc_tb.tb_lineno))
        CommonUtil.ExecLog(sModuleInfo, "Unable to start appium instance at port :%d"%port_to_connect, 3, local_run)
        return False


def launch(package_name,activity_name):
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    try:
        sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
        CommonUtil.ExecLog(sModuleInfo,"Trying to launch the app...",1,local_run)
        
        if 'driver' not in globals():
            # appium driver not initiated.
            outcome = launch_and_start_driver(package_name, activity_name)
            if outcome == "Passed":
                CommonUtil.ExecLog(sModuleInfo,"App is launched",1,local_run)
                return "Passed"
            elif outcome == "failed":
                CommonUtil.ExecLog(sModuleInfo, "App is not launched", 3,local_run)
                return "failed"
        else:
            #driver already initiated.
            CommonUtil.ExecLog(sModuleInfo,"App is launched already.",1,local_run)
            return "Passed"
            """outcome = open()
            if outcome == "Passed":
                CommonUtil.ExecLog(sModuleInfo,"App is launched",1,local_run)
                return outcome
            elif outcome == "failed":
                CommonUtil.ExecLog(sModuleInfo, "App is not launched", 3,local_run)
                return outcome"""
    
    except Exception, e:
        exc_type, exc_obj, exc_tb = sys.exc_info()        
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        Error_Detail = ((str(exc_type).replace("type ", "Error Type: ")) + ";" +  "Error Message: " + str(exc_obj) +";" + "File Name: " + fname + ";" + "Line: "+ str(exc_tb.tb_lineno))
        CommonUtil.ExecLog(sModuleInfo, "Unable to start WebDriver. %s"%Error_Detail, 3,local_run)
        return "failed"


def launch_and_start_driver(package_name, activity_name):
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    try:
        CommonUtil.ExecLog(sModuleInfo,"Trying to launch the app...",1,local_run)
        desired_caps = {}
        desired_caps['platformName'] = 'Android'
        df = adbOptions.get_android_version()
        CommonUtil.ExecLog(sModuleInfo,df,1,local_run)
        #adbOptions.kill_adb_server()
        desired_caps['platformVersion'] = df
        df = adbOptions.get_device_model()
        CommonUtil.ExecLog(sModuleInfo,df,1,local_run)
        #adbOptions.kill_adb_server()
        desired_caps['deviceName'] = df
        desired_caps['appPackage'] = package_name
        desired_caps['appActivity'] = activity_name
        driver = webdriver.Remote('http://localhost:4723/wd/hub', desired_caps)
        global driver
        CommonUtil.ExecLog(sModuleInfo,"Launched the app successfully.",1,local_run)
        wait(10)
        return "Passed"
    except Exception, e:
        exc_type, exc_obj, exc_tb = sys.exc_info()        
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        Error_Detail = ((str(exc_type).replace("type ", "Error Type: ")) + ";" +  "Error Message: " + str(exc_obj) +";" + "File Name: " + fname + ";" + "Line: "+ str(exc_tb.tb_lineno))
        CommonUtil.ExecLog(sModuleInfo, "Unable to start WebDriver. %s"%Error_Detail, 3,local_run)
        return "failed"
        
        
def close():
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    try:
        CommonUtil.ExecLog(sModuleInfo,"Trying to close the app",1,local_run)
        driver.close_app()
        CommonUtil.ExecLog(sModuleInfo,"Closed the app successfully",1,local_run)
        driver.quit()
        return "Passed"
    except Exception, e:
        exc_type, exc_obj, exc_tb = sys.exc_info()        
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        Error_Detail = ((str(exc_type).replace("type ", "Error Type: ")) + ";" +  "Error Message: " + str(exc_obj) +";" + "File Name: " + fname + ";" + "Line: "+ str(exc_tb.tb_lineno))
        CommonUtil.ExecLog(sModuleInfo, "Unable to close the driver. %s"%Error_Detail, 3,local_run)
        return "failed"
    
    
def install(app_location, app_package, app_activity):
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    try:
        sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
        CommonUtil.ExecLog(sModuleInfo,"Trying to install the app...",1,local_run)
        
        if 'driver' in globals():
            #driver initiated
            """if driver.is_app_installed(app_package):
                CommonUtil.ExecLog(sModuleInfo,"App is already installed.",1,local_run)
                return "Passed"
            else:
                CommonUtil.ExecLog(sModuleInfo,"App is not installed. Now installing...",1,local_run)"""
            outcome = load(app_location)
            if outcome == "Passed":
                CommonUtil.ExecLog(sModuleInfo,"App is installed.",1,local_run)
                return "Passed"
            elif outcome == "failed":
                CommonUtil.ExecLog(sModuleInfo, "Failed to install the app.", 3,local_run)
                return "failed"
        
        else:
            #driver not initiated
            try:
                #It will try to launch the app as if its already installed
                outcome = launch_and_start_driver(app_package, app_activity)
                if outcome == "Passed":
                    CommonUtil.ExecLog(sModuleInfo,"App is installed already.",1,local_run)
                    return "Passed"
                elif outcome == "failed":
                    CommonUtil.ExecLog(sModuleInfo, "App is not installed. Now trying to install and launch again...", 3,local_run)
                    answer = install_and_start_driver(app_location)
                    if answer == "Passed":
                        CommonUtil.ExecLog(sModuleInfo,"App is installed",1,local_run)
                        return "Passed"
                    elif answer == "failed":
                        CommonUtil.ExecLog(sModuleInfo, "Failed to install the app.", 3,local_run)
                        return "failed"
                    
            except:
                answer = install_and_start_driver(app_location)
                if answer == "Passed":
                    CommonUtil.ExecLog(sModuleInfo,"App is installed.",1,local_run)
                    return "Passed"
                elif answer == "failed":
                    CommonUtil.ExecLog(sModuleInfo, "Failed to install the app.", 3,local_run)
                    return "failed"
                    

    except Exception, e:
        exc_type, exc_obj, exc_tb = sys.exc_info()        
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        Error_Detail = ((str(exc_type).replace("type ", "Error Type: ")) + ";" +  "Error Message: " + str(exc_obj) +";" + "File Name: " + fname + ";" + "Line: "+ str(exc_tb.tb_lineno))
        CommonUtil.ExecLog(sModuleInfo, "Unable to start WebDriver. %s"%Error_Detail, 3,local_run)
        return "failed"


def install_and_start_driver(app_location):
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    try:
        CommonUtil.ExecLog(sModuleInfo,"Trying to install and then launch the app...",1,local_run)
        desired_caps = {}
        desired_caps['platformName'] = 'Android'
        df = adbOptions.get_android_version()
        CommonUtil.ExecLog(sModuleInfo,df,1,local_run)
        #adbOptions.kill_adb_server()
        desired_caps['platformVersion'] = df
        df = adbOptions.get_device_model()
        CommonUtil.ExecLog(sModuleInfo,df,1,local_run)
        #adbOptions.kill_adb_server()
        desired_caps['deviceName'] = df
        desired_caps['app'] = PATH(app_location)
        driver = webdriver.Remote('http://localhost:4723/wd/hub', desired_caps)
        global driver
        CommonUtil.ExecLog(sModuleInfo,"Installed and launched the app successfully.",1,local_run)
        time.sleep(10)
        driver.implicitly_wait(5)
        return "Passed"
    except Exception, e:
        exc_type, exc_obj, exc_tb = sys.exc_info()        
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        Error_Detail = ((str(exc_type).replace("type ", "Error Type: ")) + ";" +  "Error Message: " + str(exc_obj) +";" + "File Name: " + fname + ";" + "Line: "+ str(exc_tb.tb_lineno))
        CommonUtil.ExecLog(sModuleInfo, "Unable to start WebDriver. %s"%Error_Detail, 3,local_run)
        return "failed"


def open():
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    try:
        CommonUtil.ExecLog(sModuleInfo,"Trying to open the app",1,local_run)
        driver.launch_app()
        CommonUtil.ExecLog(sModuleInfo,"Opened the app successfully",1,local_run)
        return "Passed"
    except Exception, e:
        exc_type, exc_obj, exc_tb = sys.exc_info()        
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        Error_Detail = ((str(exc_type).replace("type ", "Error Type: ")) + ";" +  "Error Message: " + str(exc_obj) +";" + "File Name: " + fname + ";" + "Line: "+ str(exc_tb.tb_lineno))
        CommonUtil.ExecLog(sModuleInfo, "Unable to open the app. %s"%Error_Detail, 3,local_run)
        return "failed"
    
    
def load(app_location):
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    try:
        CommonUtil.ExecLog(sModuleInfo,"Trying to load the app..",1,local_run)
        #driver.install_app(app_location)
        adbOptions.install_app(app_location)
        CommonUtil.ExecLog(sModuleInfo,"Loaded the app successfully",1,local_run)
        return "Passed"
    except Exception, e:
        exc_type, exc_obj, exc_tb = sys.exc_info()        
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        Error_Detail = ((str(exc_type).replace("type ", "Error Type: ")) + ";" +  "Error Message: " + str(exc_obj) +";" + "File Name: " + fname + ";" + "Line: "+ str(exc_tb.tb_lineno))
        CommonUtil.ExecLog(sModuleInfo, "Unable to load the app. %s"%Error_Detail, 3,local_run)
        return "failed"
    

def reset():
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    try:
        CommonUtil.ExecLog(sModuleInfo,"Trying to reset the app...",1,local_run)
        driver.reset()
        wait(5)
        CommonUtil.ExecLog(sModuleInfo,"App is reset successfully",1,local_run)
        return "Passed"
    except Exception, e:
        exc_type, exc_obj, exc_tb = sys.exc_info()        
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        Error_Detail = ((str(exc_type).replace("type ", "Error Type: ")) + ";" +  "Error Message: " + str(exc_obj) +";" + "File Name: " + fname + ";" + "Line: "+ str(exc_tb.tb_lineno))
        CommonUtil.ExecLog(sModuleInfo, "Unable to reset the app. %s"%Error_Detail, 3,local_run)
        return "failed"
    
    
def go_back():
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    try:
        CommonUtil.ExecLog(sModuleInfo,"Trying to go back...",1,local_run)
        driver.back()
        CommonUtil.ExecLog(sModuleInfo,"Went back successfully",1,local_run)
        return "Passed"
    except Exception, e:
        exc_type, exc_obj, exc_tb = sys.exc_info()        
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        Error_Detail = ((str(exc_type).replace("type ", "Error Type: ")) + ";" +  "Error Message: " + str(exc_obj) +";" + "File Name: " + fname + ";" + "Line: "+ str(exc_tb.tb_lineno))
        CommonUtil.ExecLog(sModuleInfo, "Unable to go back. %s"%Error_Detail, 3,local_run)
        return "failed"

    
def wait(_time):
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    try:
        CommonUtil.ExecLog(sModuleInfo,"Starting waiting for %s seconds.."%_time,1,local_run)
        driver.implicitly_wait(_time)
        time.sleep(_time)
        CommonUtil.ExecLog(sModuleInfo,"Waited successfully",1,local_run)
        return "Passed"
    except Exception, e:
        exc_type, exc_obj, exc_tb = sys.exc_info()        
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        Error_Detail = ((str(exc_type).replace("type ", "Error Type: ")) + ";" +  "Error Message: " + str(exc_obj) +";" + "File Name: " + fname + ";" + "Line: "+ str(exc_tb.tb_lineno))
        CommonUtil.ExecLog(sModuleInfo, "Unable to wait. %s"%Error_Detail, 3,local_run)
        return "failed"

    
def remove(app_package):
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    try:
        CommonUtil.ExecLog(sModuleInfo,"Trying to remove app with package name %s..."%app_package,1,local_run)
        #if driver.is_app_installed(app_package):
            #CommonUtil.ExecLog(sModuleInfo,"App is installed. Now removing...",1,local_run)
        try:
            driver.remove_app(app_package)
            CommonUtil.ExecLog(sModuleInfo,"App is removed successfully.",1,local_run)
            return "Passed"
        except:
            CommonUtil.ExecLog(sModuleInfo, "Unable to remove the app", 3,local_run)
            return "failed"
        """else:   
            CommonUtil.ExecLog(sModuleInfo,"App is not found.",3,local_run)
            return "failed" """
        
    except Exception, e:
        exc_type, exc_obj, exc_tb = sys.exc_info()        
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        Error_Detail = ((str(exc_type).replace("type ", "Error Type: ")) + ";" +  "Error Message: " + str(exc_obj) +";" + "File Name: " + fname + ";" + "Line: "+ str(exc_tb.tb_lineno))
        CommonUtil.ExecLog(sModuleInfo, "Unable to wait. %s"%Error_Detail, 3,local_run)
        return "failed"


