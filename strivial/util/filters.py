from flask import current_app as app

'''
given a total number of seconds, give a duration broken into hours, minutes and optionally seconds
'''
@app.template_filter()
def format_seconds(value, display_seconds=False):
    hours, rem = divmod(value, 3600)
    minutes, seconds = divmod(rem, 60)

    formatted_duration = ""
    if hours > 0:
        formatted_duration += "{}h".format(int(hours))
    if not display_seconds and minutes > 0:
        formatted_duration += "{}m".format(int(minutes))
    if display_seconds and minutes > 0:
        formatted_duration += "{0}:{1}".format(int(minutes), int(seconds))

    return formatted_duration