def check_premium_access(user):
    return getattr(user, 'is_premium', False)

def can_create_entry(user):
    # Example: Only allow 50 entries for free users
    if check_premium_access(user):
        return True
    return user.diaryentry_set.count() < 50

