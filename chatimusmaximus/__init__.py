import os
import yaml
import logging

import yapsy.ConfigurablePluginManager import ConfigurablePluginManager
import plugins

def get_lisetners():
    plugin_manager = ConfigurablePluginManager(yaml.load, categories_filter={'Listeners': plugins.listeners.base_plugin.Base})

    file_dir = os.path.dirname(os.path.dirname(__file__))
    plugin_path = os.path.join(file_dir, '..', 'plugin', 'listeners')
    plugin_manager.setPluginPlaces([plugin_path])
    plugin_manager.collectPlugins()
    result = []
    for plugin_info in plugin_manager.getAllPlugins():

def get_settings_helper():
    """
    This helper loads the information from the file
    and works with the versioning information in the settings
    """
    # get the main directory
    main_dir = os.path.dirname(os.path.realpath(__file__))
    # get our default filepath and perferred filepath names using main dir
    default_filename = os.path.join(main_dir, 'default_settings.yml')
    perferred_filename = os.path.join(main_dir, 'settings.yml')
    
    # open the default file and get version information
    with open(default_filename) as default_filestream:
        default_filesettings = yaml.load(default_filestream)

    # get the settings version out and split on the `.` operator
    default_version = default_filesettings['version'].split('.')
    
    # allow our user to put info in default_settings.yml or settings.yml
    if os.path.exists(perferred_filename):
        filename = perferred_filename
    else:
        filename = default_filename

    with open(filename) as setting_file:    
        settings = yaml.load(setting_file)
    # get the settings version out and split on the `.` operator
    settings_version = settings.pop('version').split('.')
    if not settings_version[0] == default_version[0] or not settings_version[1] == default_version[1]: 
        # TODO: add in logic to help user migrate changes
        print('Settings file has changed, please update {}'.format(filename))
    return settings

def validate_settings_not_blank(setting):
    settings_have_values = False
    for key, value in setting.items():
        if value == str() or key == 'display_settings' or key == 'connect':
            pass
        else:
            settings_have_values = True
            break
    return settings_have_values

def instantiate_chats_helper(settings):
    """
    This helper parses through the settings and 
    and instantiates all of the used chats
    """
    log = logging.getLogger()
    # create the list to return
    chat_site_list = []
    plugins.get_website_plugins()
    # parse the plugins to just get the names
    str_plugins = [str(s).split('.')[0].split('/')[-1] for s in plugins.IWebsitePluginRegistry.plugins]

    # now check the settings keys and if any keys are found
    # that match the plugins, instantiate the plugin
    for settings_key, setting in settings.items():
        has_values = validate_settings_not_blank(setting)

        # NOTE: This removes the setting COMPLETELY if it doesn't have values and isn't meant to be displayed
        # remove setting if it doesn't have values and not dispaly_missing
        if not has_values and not setting['display_settings']['display_missing']:
            removed_plugin = settings.pop(settings_key)
            log.info('Plugin {} not being used'.format(removed_plugin))

        # check to see if  are registered in plugins
        if settings_key in str_plugins and has_values and setting['connect']:
            # find the index
            index = str_plugins.index(settings_key)
            # grab the class instance
            kls = plugins.IWebsitePluginRegistry.plugins[index]
            # settings is a dict, so pass the key back in to get the settings
            instantiate_plugin = kls(settings[settings_key])
            # lastly, push the instantiated plugin onto list
            chat_site_list.append(instantiate_plugin)

    return chat_site_list
