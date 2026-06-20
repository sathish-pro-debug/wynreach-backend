def calculate_reputation(tenant):

    if tenant.total_sent == 0:
        return 100

    bounce_rate = (
        tenant.total_bounces / tenant.total_sent
    ) * 100

    complaint_rate = (
        tenant.total_complaints / tenant.total_sent
    ) * 100

    score = 100

    score -= bounce_rate * 5

    score -= complaint_rate * 50

    if score < 0:
        score = 0

    return score