config = {
    "device": {"rtype": "device", "rid": "9d6d3d0c-2c30-4369-af41-e3a09866da62"}, 
    "button1": {"where": [{"group": {"rtype": "room", "rid": "14abc0ae-04bd-5cb3-9b6d-c1d807840eba"}}], "on_short_release": {"action": "all_off"}, "on_long_press": {"action": "all_off"}}, 
    "button2": {"where": [{"group": {"rtype": "room", "rid": "46332c14-1c72-5fe3-b817-9621e535a68b"}}], "on_short_release": {"action": "all_off"}, "on_long_press": {"action": "all_off"}}, 
    "button3": {"where": [{"group": {"rtype": "room", "rid": "3cc5085e-402f-55cb-b787-3c0bc79891b7"}}], "on_short_release": {"action": "all_off"}, "on_long_press": {"action": "all_off"}}, 
    "button4": {"where": [{"group": {"rtype": "room", "rid": "93be80b5-5811-56ff-b497-16309aecec29"}}], "on_short_release": {"action": "all_off"}, "on_long_press": {"action": "all_off"}}, 
    "rotary": {"where": [{"group": {"rtype": "room", "rid": "f3d802e9-49a9-5724-b9ca-0480f1f3f8bb"}}], "on_dim_off": {"action": "all_off"}, "on_dim_on": {"recall_single": [{"action": {"recall": {"rtype": "scene", "rid": "af980227-d0ae-43d8-9bd5-4ccf54e00b1e"}}}]}}}


#{'type': 'behavior_instance', 'metadata': {'type': 'instance_metadata', 'name': 'Gang'}, 'script_id': '67d9395b-4403-42cc-b5f0-740b699d67c6', 'enabled': True, 
# 'configuration': 
# {'device': {'rtype': 'device', 'rid': 'bccd5a04-17ae-4e0b-89f6-5ec5d4b0eb5b'}, 
#                   'where': [{'group': {'rtype': 'room', 'rid': '14abc0ae-04bd-5cb3-9b6d-c1d807840eba'}}], 
#                   'buttons': {'61886af4-b24c-5069-b812-33970df76224': {'on_short_release': {'time_based_extended': {'slots': [{'start_time': {'hour': 7, 'minute': 0}, 'actions': [{'action': {'recall': {'rtype': 'scene', 'rid': 'd94c0525-2cc5-4580-aafe-e8d81a07201b'}}}]}, {'start_time': {'hour': 10, 'minute': 0}, 'actions': [{'action': {'recall': {'rtype': 'scene', 'rid': 'd94c0525-2cc5-4580-aafe-e8d81a07201b'}}}]}, {'start_time': {'hour': 17, 'minute': 0}, 'actions': [{'action': {'recall': {'rtype': 'scene', 'rid': 'd94c0525-2cc5-4580-aafe-e8d81a07201b'}}}]}, {'start_time': {'hour': 20, 'minute': 0}, 'actions': [{'action': {'recall': {'rtype': 'scene', 'rid': '09dbce66-71f2-4600-8d75-068831534b44'}}}]}, {'start_time': {'hour': 23, 'minute': 0}, 'actions': [{'action': {'recall': {'rtype': 'scene', 'rid': '0ee92fe9-76ad-44b5-a128-be4aa2ec2553'}}}]}], 'with_off': {'enabled': False}}}, 'on_long_press': {'action': 'do_nothing'}}, 'a246a491-6307-5880-a3f3-30cadc3c05da': {'on_repeat': {'action': 'dim_up'}}, 'd98bf5c8-d3ed-5ef9-80b0-7ea9bfaca383': {'on_repeat': {'action': 'dim_down'}}, '04c79bd1-3ba2-5697-a245-f15d6b486f46': {'on_short_release': {'action': 'all_off'}, 'on_long_press': {'action': 'do_nothing'}}}, 'model_id': 'RWL021'}}

#{'device': {'rtype': 'device', 'rid': 'bccd5a04-17ae-4e0b-89f6-5ec5d4b0eb5b'}, 
# 'where': [{'group': {'rtype': 'room', 'rid': '14abc0ae-04bd-5cb3-9b6d-c1d807840eba'}}], 
# 'buttons': {'61886af4-b24c-5069-b812-33970df76224': {'on_short_release': {'time_based_extended': {'slots': [{'start_time': {'hour': 7, 'minute': 0}, 'actions': [{'action': {'recall': {'rtype': 'scene', 'rid': 'd94c0525-2cc5-4580-aafe-e8d81a07201b'}}}]}, {'start_time': {'hour': 10, 'minute': 0}, 'actions': [{'action': {'recall': {'rtype': 'scene', 'rid': 'd94c0525-2cc5-4580-aafe-e8d81a07201b'}}}]}, {'start_time': {'hour': 17, 'minute': 0}, 'actions': [{'action': {'recall': {'rtype': 'scene', 'rid': 'd94c0525-2cc5-4580-aafe-e8d81a07201b'}}}]}, {'start_time': {'hour': 20, 'minute': 0}, 'actions': [{'action': {'recall': {'rtype': 'scene', 'rid': '09dbce66-71f2-4600-8d75-068831534b44'}}}]}, {'start_time': {'hour': 23, 'minute': 0}, 'actions': [{'action': {'recall': {'rtype': 'scene', 'rid': '0ee92fe9-76ad-44b5-a128-be4aa2ec2553'}}}]}], 'with_off': {'enabled': False}}}, 'on_long_press': {'action': 'do_nothing'}}, 'a246a491-6307-5880-a3f3-30cadc3c05da': {'on_repeat': {'action': 'dim_up'}}, 'd98bf5c8-d3ed-5ef9-80b0-7ea9bfaca383': {'on_repeat': {'action': 'dim_down'}}, '04c79bd1-3ba2-5697-a245-f15d6b486f46': {'on_short_release': {'action': 'all_off'}, 'on_long_press': {'action': 'do_nothing'}}}, 'model_id': 'RWL021'}


#for device in config:
#    print(config[device]["where"])
name = "Hue Motion Sensor"
print(name[:14])
