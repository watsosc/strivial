from flask import current_app as app

# given a total number of seconds, give a duration broken into hours, minutes and optionally seconds
@app.template_filter()
def format_seconds(value, display_seconds=False):
    hours, rem = divmod(value, 3600)
    minutes, seconds = divmod(rem, 60)

    formatted_duration = "{0}h{1}m".format(int(hours), int(minutes))
    if display_seconds:
        formatted_duration += ":{}".format(int(seconds))

    return formatted_duration