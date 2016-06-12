from mpf.core.config_player import ConfigPlayer
from mpf.core.utility_functions import Util


class LightPlayer(ConfigPlayer):
    config_file_section = 'light_player'
    show_section = 'lights'
    machine_collection_name = 'lights'

    def play(self, settings, context, priority=0, **kwargs):
        del kwargs
        instance_dict = self._get_instance_dict(context)
        full_context = self._get_full_context(context)

        if 'lights' in settings:
            settings = settings['lights']

        for light, s in settings.items():
            try:
                s['priority'] += priority
            except KeyError:
                s['priority'] = priority

            try:
                light.on(key=full_context, **s)
                instance_dict[light.name] = light

            except AttributeError:
                try:
                    self._light_on(light, instance_dict, full_context, **s)
                except KeyError:
                    light_list = Util.string_to_list(light)
                    if len(light_list) > 1:
                        for light1 in light_list:
                            self._light_on(light1, instance_dict, full_context, **s)
                    else:
                        for light1 in self.machine.lights.sitems_tagged(light):
                            self._light_on(light1, instance_dict, full_context, **s)

    def _light_on(self, light_name, instance_dict, full_context, **s):
        light = self.machine.lights[light_name]
        light.on(key=full_context, **s)
        instance_dict[light.name] = light

    def clear_context(self, context):
        full_context = self._get_full_context(context)
        for light in self._get_instance_dict(context).values():
            light.remove_from_stack_by_key(full_context)

    def get_express_config(self, value):
        value = str(value).replace(' ', '').lower()
        fade = 0
        if '-f' in value:
            composite_value = value.split('-f')
            value = composite_value[0]
            fade = Util.string_to_ms(composite_value[1])

        return dict(brightness=value, fade=fade)

    def get_full_config(self, value):
        super().get_full_config(value)
        value['fade_ms'] = value.pop('fade')
        return value

player_cls = LightPlayer
