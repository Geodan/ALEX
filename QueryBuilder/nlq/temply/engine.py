
class TypeTemplateExtracter(object):

    def __init__(self):
        self.templates = []

    def add_template(self, template, new):
        template_length = len(template)
        self.templates.append((template, new))
        self.templates.sort(key=lambda t: len(t[0]), reversed=True)

    def extract_all_templates(self, objects, extract):
        old_objects = objects
        new_objects = []

        if preprocess:
            objects = [type(o) for o in objects]

        for obj_index, o in enumerate(objects):

            # Template found on current object
            templated = False

            for templ_index, template in enumerate(self.templates):
                extraction = {}
                mistake_found = False

                for i in range(0, len(template[0])):

                    if (obj_index + i) >= len(objects):
                        mistake_found = True
                        break
                    if template[0][i] != objects[obj_index + i]:
                        mistake_found = True
                        break

                    for extract_index, argument in enumerate(extract):
                        if argument[0] == i:
                            extraction[argument[1]] = old_objects[obj_index]

                if not mistake_found:
                    templated = True
                    new_objects.append(template[1](extraction))

            if not templated:
                new_objects.append(old_objects[obj_index])
