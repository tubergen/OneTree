def notify_processor(request):
    new_notif_bool = False
    if request.user.is_authenticated():
        new_notif_bool = request.user.get_profile().has_new_notifs()
    return {'new_notif': new_notif_bool}
