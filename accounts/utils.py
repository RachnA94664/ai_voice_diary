from datetime import date, datetime, timedelta


# --------------------------------------------------
# PREMIUM / TRIAL CHECK
# --------------------------------------------------
def check_premium_access(user):
    """
    Returns True if the user is:
    - premium, or
    - in an active trial period
    """
    profile = getattr(user, 'userprofile', None)
    if not profile:
        return False

    # Premium user
    if getattr(profile, 'is_premium', False):
        return True

    # Trial user
    if profile.subscription_type == 'trial':
        if profile.trial_end_date and profile.trial_end_date >= datetime.now():
            return True

    return False


# --------------------------------------------------
# TRIAL DAYS LEFT
# --------------------------------------------------
def get_trial_days_left(user):
    """
    Returns the number of days remaining in the trial.
    Returns 0 if:
    - no profile
    - no trial_end_date
    - trial already ended
    """
    profile = getattr(user, 'userprofile', None)
    if not profile or not profile.trial_end_date:
        return 0

    today = date.today()
    trial_end = profile.trial_end_date.date()

    return max((trial_end - today).days, 0)


# --------------------------------------------------
# DAILY CHAT QUESTION LIMIT (FOR FREE USERS)
# --------------------------------------------------
def increment_chat_questions(user):
    """
    Increments the user's daily chat question count.
    Resets the count if it's a new day.
    """
    profile = getattr(user, 'userprofile', None)
    if not profile:
        return

    today = date.today()

    # Reset count if new day
    if profile.chat_questions_date != today:
        profile.chat_questions_date = today
        profile.chat_questions_today = 1
    else:
        profile.chat_questions_today += 1

    profile.save()


# --------------------------------------------------
# ENTRY CREATION LIMIT
# --------------------------------------------------
def can_create_entry(user):
    """
    Returns True if:
    - user is premium or trial
    - OR user is free and entry_count < limit
    """

    profile = getattr(user, 'userprofile', None)
    if not profile:
        return False

    # Premium or trial user → unlimited entries
    if check_premium_access(user):
        return True

    # Free user limit (modify as needed)
    FREE_LIMIT = 50

    return profile.entry_count < FREE_LIMIT
