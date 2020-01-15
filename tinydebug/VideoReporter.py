import inspect
import os
import cv2
import numpy
import yaml
from PIL import Image, ImageDraw, ImageFont
import textwrap


class VideoReporter:
    """Reporter class, reports program execution results to as a video."""

    def __init__(self, func, results, config_path):
        self.source_lines, self.start_line = inspect.getsourcelines(func)
        self.results = results
        with open(config_path) as config_file:
            self.config = yaml.safe_load(config_file)
            with open(os.path.dirname(__file__) + "/color_themes/" + self.config["theme"] + ".yaml") as theme_file:
                self.color_theme = yaml.safe_load(theme_file)

    def __wrap_text(self, font, text, max_width):
        num_chars = len(text)
        while font.getsize_multiline(textwrap.fill(text, num_chars))[0] >= max_width:
            num_chars -= 1

        return textwrap.fill(text, num_chars)

    def __draw_intro_text(self):
        intro_text = self.config["intro-text"]["text"]
        frame_size = (self.config["size"]["width"], self.config["size"]["height"])
        img = Image.new("RGB", frame_size, color=self.color_theme["background-color"])

        font = ImageFont.truetype(os.path.dirname(__file__) + "/fonts/{}.ttf".format(self.config["fonts"]["intro-text"]["font-family"]),
                                  self.config["fonts"]["intro-text"]["font-size"])
        draw = ImageDraw.Draw(img)

        intro_text = self.__wrap_text(font, intro_text, frame_size[0] * 0.8)
        intro_text_size = font.getsize_multiline(intro_text)
        text_start_x, text_start_y = (frame_size[0] - intro_text_size[0]) / 2, (frame_size[1] - intro_text_size[1]) / 2

        draw.text((text_start_x, text_start_y), intro_text, font=font, fill=self.color_theme["text-color"])

        return img

    def __draw_frame(self, current_step, variable_history):
        """
        Draws the current frame in the video.

        :param current_step: The current step in the execution log.
        :param variable_history: The entire variable history.
        :param (int, int) frame_size: The frame size as (width, height) in pixels.
        :param int font_size: Font size in pts.
        :return: The current frame as a Pillow image.
        """

        font_size = self.config["fonts"]["default"]["font-size"]
        frame_size = (self.config["size"]["width"], self.config["size"]["height"])

        img = Image.new("RGB", frame_size, color=self.color_theme["background-color"])

        font = ImageFont.truetype(os.path.dirname(__file__) + "/fonts/{}.ttf".format(self.config["fonts"]["default"]["font-family"]), self.config["fonts"]["default"]["font-size"])
        draw = ImageDraw.Draw(img)

        # Source code section
        draw.rectangle((0, (current_step['line_num'] - self.start_line) * font_size, frame_size[0] * 0.4, (current_step['line_num'] - self.start_line + 1) * font_size),
                       fill=self.color_theme["current-line-color"])
        for line_offset, line in enumerate(self.source_lines):
            draw.text((0, line_offset * font_size), self.source_lines[line_offset], font=font, fill=self.color_theme["text-color"])

        # Step section
        draw.text((0, frame_size[1] * 0.8), "Step: {}, line: {}".format(current_step['step'], current_step['line_num']), font=font, fill=self.color_theme["text-color"])
        draw.text((0, frame_size[1] * 0.8 + font_size),
                  "Times executed: {}, time spent: {}".format(current_step['line_runtime']['times_executed'], "{0:.2f}".format(current_step['line_runtime']['total_time'])),
                  font=font, fill=self.color_theme["text-color"])

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
                draw.text((frame_size[0] * 0.4 + 5, current_text_y), message, font=font, fill=self.color_theme["changed-variable-color"])
            elif curr_value is not None:
                draw.text((frame_size[0] * 0.4 + 5, current_text_y), "Variable {}, value {}.".format(variable['var'], curr_value), font=font, fill=self.color_theme["text-color"])
            current_text_y += font_size

        # Vertical and horizontal split lines
        line_color = self.color_theme["separating-line-color"]
        draw.line((frame_size[0] * 0.4, 0, frame_size[0] * 0.4, frame_size[1]), fill=line_color, width=5)
        draw.line((0, frame_size[1] * 0.8, frame_size[0] * 0.4, frame_size[1] * 0.8), fill=line_color, width=5)

        # Watermark
        print(self.config["watermark"])
        if self.config["watermark"]:
            watermark_font = ImageFont.truetype(os.path.dirname(__file__) + "/fonts/OpenSansBold.ttf", 22)
            text_width, text_height = watermark_font.getsize("Created using TinyDebug")
            draw.text((frame_size[0] - text_width, frame_size[1] - text_height), "Created using TinyDebug", font=watermark_font, fill=self.color_theme["text-color"])

        return img

    def generate_video(self, output_path):
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')

        frame_size = (self.config["size"]["width"], self.config["size"]["height"])
        fps = self.config["fps"]
        video = cv2.VideoWriter(output_path, fourcc, fps, frame_size)

        if self.config["intro-text"]["text"]:
            intro_img = self.__draw_intro_text()
            num_intro_frames = fps * self.config["intro-text"]["time"]
            for _ in range(num_intro_frames):
                video.write(cv2.cvtColor(numpy.array(intro_img), cv2.COLOR_RGB2BGR))

        for step in self.results["execution_log"]:
            img = self.__draw_frame(step, self.results["variable_history"])
            video.write(cv2.cvtColor(numpy.array(img), cv2.COLOR_RGB2BGR))

        video.release()
