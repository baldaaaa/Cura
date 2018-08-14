# Copyright (c) 2018 Ultimaker B.V.
# Cura is released under the terms of the LGPLv3 or higher.

import os #To find the directory with test files and find the test files.
import unittest.mock #To mock and monkeypatch stuff.

from cura.Settings.ExtruderStack import ExtruderStack #Testing for returning the correct types of stacks.
from cura.Settings.GlobalStack import GlobalStack #Testing for returning the correct types of stacks.
import UM.Settings.InstanceContainer #Creating instance containers to register.
import UM.Settings.ContainerRegistry #Making empty container stacks.
import UM.Settings.ContainerStack #Setting the container registry here properly.

def teardown():
    #If the temporary file for the legacy file rename test still exists, remove it.
    temporary_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "stacks", "temporary.stack.cfg")
    if os.path.isfile(temporary_file):
        os.remove(temporary_file)

##  Tests whether addContainer properly converts to ExtruderStack.
def test_addContainerExtruderStack(container_registry, definition_container):
    container_registry.addContainer(definition_container)

    container_stack = UM.Settings.ContainerStack.ContainerStack(stack_id = "Test Extruder Stack") #A container we're going to convert.
    container_stack.setMetaDataEntry("type", "extruder_train") #This is now an extruder train.
    container_stack.insertContainer(0, definition_container) #Add a definition to it so it doesn't complain.

    mock_super_add_container = unittest.mock.MagicMock() #Takes the role of the Uranium-ContainerRegistry where the resulting containers get registered.
    with unittest.mock.patch("UM.Settings.ContainerRegistry.ContainerRegistry.addContainer", mock_super_add_container):
        container_registry.addContainer(container_stack)

    assert len(mock_super_add_container.call_args_list) == 2 #Called only once.
    assert len(mock_super_add_container.call_args_list[1][0]) == 1 #Called with one parameter.
    assert type(mock_super_add_container.call_args_list[1][0][0]) == ExtruderStack

##  Tests whether addContainer properly converts to GlobalStack.
def test_addContainerGlobalStack(container_registry, definition_container):
    container_registry.addContainer(definition_container)

    container_stack = UM.Settings.ContainerStack.ContainerStack(stack_id = "Test Global Stack") #A container we're going to convert.
    container_stack.setMetaDataEntry("type", "machine") #This is now a global stack.
    container_stack.insertContainer(0, definition_container) #Must have a definition.

    mock_super_add_container = unittest.mock.MagicMock() #Takes the role of the Uranium-ContainerRegistry where the resulting containers get registered.
    with unittest.mock.patch("UM.Settings.ContainerRegistry.ContainerRegistry.addContainer", mock_super_add_container):
        container_registry.addContainer(container_stack)

    assert len(mock_super_add_container.call_args_list) == 2 #Called only once.
    assert len(mock_super_add_container.call_args_list[1][0]) == 1 #Called with one parameter.
    assert type(mock_super_add_container.call_args_list[1][0][0]) == GlobalStack

def test_addContainerGoodSettingVersion(container_registry, definition_container):
    from cura.CuraApplication import CuraApplication
    definition_container.getMetaData()["setting_version"] = CuraApplication.SettingVersion
    container_registry.addContainer(definition_container)

    instance = UM.Settings.InstanceContainer.InstanceContainer(container_id = "Test Instance Right Version")
    instance.setMetaDataEntry("setting_version", CuraApplication.SettingVersion)
    instance.setDefinition(definition_container.getId())

    mock_super_add_container = unittest.mock.MagicMock() #Take the role of the Uranium-ContainerRegistry where the resulting containers get registered.
    with unittest.mock.patch("UM.Settings.ContainerRegistry.ContainerRegistry.addContainer", mock_super_add_container):
        container_registry.addContainer(instance)

    mock_super_add_container.assert_called_once_with(instance) #The instance must have been registered now.

def test_addContainerNoSettingVersion(container_registry, definition_container):
    from cura.CuraApplication import CuraApplication
    definition_container.getMetaData()["setting_version"] = CuraApplication.SettingVersion
    container_registry.addContainer(definition_container)

    instance = UM.Settings.InstanceContainer.InstanceContainer(container_id = "Test Instance No Version")
    #Don't add setting_version metadata.
    instance.setDefinition(definition_container.getId())

    mock_super_add_container = unittest.mock.MagicMock() #Take the role of the Uranium-ContainerRegistry where the resulting container should not get registered.
    with unittest.mock.patch("UM.Settings.ContainerRegistry.ContainerRegistry.addContainer", mock_super_add_container):
        container_registry.addContainer(instance)

    mock_super_add_container.assert_not_called() #Should not get passed on to UM.Settings.ContainerRegistry.addContainer, because the setting_version is interpreted as 0!

def test_addContainerBadSettingVersion(container_registry, definition_container):
    from cura.CuraApplication import CuraApplication
    definition_container.getMetaData()["setting_version"] = CuraApplication.SettingVersion
    container_registry.addContainer(definition_container)

    instance = UM.Settings.InstanceContainer.InstanceContainer(container_id = "Test Instance Wrong Version")
    instance.setMetaDataEntry("setting_version", 9001) #Wrong version!
    instance.setDefinition(definition_container.getId())

    mock_super_add_container = unittest.mock.MagicMock() #Take the role of the Uranium-ContainerRegistry where the resulting container should not get registered.
    with unittest.mock.patch("UM.Settings.ContainerRegistry.ContainerRegistry.addContainer", mock_super_add_container):
        container_registry.addContainer(instance)

    mock_super_add_container.assert_not_called() #Should not get passed on to UM.Settings.ContainerRegistry.addContainer, because the setting_version doesn't match its definition!

##  Tests whether loading gives objects of the correct type.
# @pytest.mark.parametrize("filename,                  output_class", [
#                         ("ExtruderLegacy.stack.cfg", ExtruderStack),
#                         ("MachineLegacy.stack.cfg",  GlobalStack),
#                         ("Left.extruder.cfg",        ExtruderStack),
#                         ("Global.global.cfg",        GlobalStack),
#                         ("Global.stack.cfg",         GlobalStack)
# ])
# def test_loadTypes(filename, output_class, container_registry):
#     #Mock some dependencies.
#     Resources.getAllResourcesOfType = unittest.mock.MagicMock(return_value = [os.path.join(os.path.dirname(os.path.abspath(__file__)), "stacks", filename)]) #Return just this tested file.
#
#     def findContainers(container_type = 0, id = None):
#         if id == "some_instance":
#             return [UM.Settings.ContainerRegistry._EmptyInstanceContainer(id)]
#         elif id == "some_definition":
#             return [DefinitionContainer(container_id = id)]
#         else:
#             return []
#
#     container_registry.findContainers = findContainers
#
#     with unittest.mock.patch("cura.Settings.GlobalStack.GlobalStack.findContainer"):
#         with unittest.mock.patch("os.remove"):
#             container_registry.load()
#
#     #Check whether the resulting type was correct.
#     stack_id = filename.split(".")[0]
#     for container_id, container in container_registry._containers.items(): #Stupid ContainerRegistry class doesn't expose any way of getting at this except by prodding the privates.
#         if container_id == stack_id: #This is the one we're testing.
#             assert type(container) == output_class
#             break
#     else:
#         assert False #Container stack with specified ID was not loaded.
