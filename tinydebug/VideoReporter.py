import inspect
from PIL import Image, ImageDraw, ImageFont
import cv2
import numpy
import os


class VideoReporter:
    """Reporter class, reports program execution results to as a video."""

    def __init__(self, func, results):
        self.source_lines, self.start_line = inspect.getsourcelines(func)
        self.results = results

    def __draw_frame(self, current_step, variable_history, frame_size, font_size):
        """
        Draws the current frame in the video.

        :param current_step: The current step in the execution log.
        :param variable_history: The entire variable history.
        :param (int, int) frame_size: The frame size as (width, height) in pixels.
        :param int font_size: Font size in pts.
        :return: The current frame as a Pillow image.
        """
        background_color = (40, 42, 54)
        current_line_color = (68, 71, 90)
        text_color = (248, 248, 242)
        changed_variable_color = (80, 250, 123)

        img = Image.new("RGB", frame_size, color=background_color)
        font = ImageFont.truetype(os.path.dirname(__file__) + "/fonts/SourceCodePro.ttf", font_size)
        draw = ImageDraw.Draw(img)

        # Source code section
        draw.rectangle((0, (current_step['line_num'] - self.start_line) * font_size, frame_size[0] * 0.4, (current_step['line_num'] - self.start_line + 1) * font_size),
                       fill=current_line_color)
        for line_offset, line in enumerate(self.source_lines):
            draw.text((0, line_offset * font_size), self.source_lines[line_offset], font=font, fill=text_color)

        # Step section
        draw.text((0, frame_size[1] * 0.8), "Step: {}, line: {}".format(current_step['step'], current_step['line_num']), font=font, fill=text_color)
        draw.text((0, frame_size[1] * 0.8 + font_size),
                  "Times executed: {}, time spent: {}".format(current_step['line_runtime']['times_executed'], "{0:.2f}".format(current_step['line_runtime']['total_time'])),
                  font=font, fill=text_color)

        # Variable section
        current_text_y = 0
        variable_changes = {}
        for action in current_step["actions"]:
            action_desc = "Illegal action"
            if action["action"] == "init_var":
                action_desc = "created"
            elif action["action"] == "change_var":
                action_desc = "previous value {}".format(action["prev_val"])
            elif action["action"] == "list_add":
                action_desc = "{}[{}] appended with value {}".format(action["var"], action["index"], action["val"])
            elif action["action"] == "list_change":
                action_desc = "{}[{}] changed from {} to {}".format(action["var"], action["index"], action["prev_val"], action["new_val"])
            elif action["action"] == "list_remove":
                action_desc = "{}[{}] removed".format(action["var"], action["index"])
            elif action["action"] == "dict_add":
                action_desc = "key {} added with value {}".format(action["key"], action["val"])
            elif action["action"] == "dict_change":
                action_desc = "value of key {} changed from {} to {}".format(action["key"], action["prev_val"], action["new_val"])
            elif action["action"] == "dict_remove":
                action_desc = "key {} removed".format(action["key"])

            if action["var"] not in variable_changes:
                variable_changes[action["var"]] = []
            variable_changes[action["var"]].append(action_desc)

        for variable in variable_history:
            curr_value = None
            for val in variable['val_history']:
                if val['step'] > current_step['step']:
                    break
                curr_value = val["value"]

            if variable['var'] in variable_changes:
                message = "Variable {}, value {}, ".format(variable['var'], curr_value) + ", ".join(variable_changes[variable['var']]) + "."
                draw.text((frame_size[0] * 0.4 + 5, current_text_y), message, font=font, fill=changed_variable_color)
            elif curr_value is not None:
                draw.text((frame_size[0] * 0.4 + 5, current_text_y), "Variable {}, value {}.".format(variable['var'], curr_value), font=font, fill=text_color)
            current_text_y += font_size

        # Vertical and horizontal split lines
        draw.line((frame_size[0] * 0.4, 0, frame_size[0] * 0.4, frame_size[1]), fill=(255, 255, 255), width=5)
        draw.line((0, frame_size[1] * 0.8, frame_size[0] * 0.4, frame_size[1] * 0.8), fill=(255, 255, 255), width=5)

        return img

    def generate_video(self, output_path, frame_size=(2000, 1000), font_size=22, fps=1):
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        video = cv2.VideoWriter(output_path, fourcc, fps, frame_size)

        for step in self.results["execution_log"]:
            img = self.__draw_frame(step, self.results["variable_history"], frame_size, font_size)
            video.write(cv2.cvtColor(numpy.array(img), cv2.COLOR_RGB2BGR))

        video.release()
