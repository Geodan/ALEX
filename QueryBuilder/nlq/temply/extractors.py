
class WordTypeTemplateExtractor(object):

    def __init__(self):
        self.templates = []

    def add_template(self, template, extract, new):
        template_length = len(template)
        self.templates.append((template, extract, new))
        self.templates.sort(key=lambda t: len(t[0]), reverse=True)

    def extract_all_templates(self, objects, context):
        old_objects = objects
        print(old_objects)

        # The new objects that replaced the old values
        result = []

        # The new array, with the objects replaced
        new_list = []

        # Checking on types, so preprocessing the objects
        objects = [type(o) for o in objects]

        # Current index in the object loop
        obj_index = 0

        while obj_index < len(objects):

            # Current object
            o = objects[obj_index]

            # Template found on current object
            templated = False

            for templ_index, template in enumerate(self.templates):

                extraction = {}
                mistake_found = False

                # Counter for skipping indices
                counter = 0

                for i in range(0, len(template[0])):

                    if (obj_index + i) >= len(objects):
                        mistake_found = True
                        break
                    if template[0][i] != objects[obj_index + i]:
                        mistake_found = True
                        break

                    for extract_index, arg in enumerate(template[1]):
                        if arg[0] == i:
                            extraction[arg[1]] = old_objects[obj_index + i]

                    counter += 1

                if not mistake_found:

                    obj_index += counter
                    counter = 0

                    templated = True
                    to_add = template[2](extraction, context)
                    new_list.append(to_add)
                    result.append(to_add)
                    break

            if not templated:
                print(len(old_objects), obj_index)
                new_list.append(old_objects[obj_index])
                obj_index += 1

        return (result, new_list)
