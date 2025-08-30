def get_responder(request):
    """
    获取审批人: 如果是部门leader, 审批人则为该部门的管理者 (董事会的leader最大, 再无更大的leader)
    """
    user = request.user
    #
    if user.department.leader.uid == user.uid:
        if user.department.name == "董事会":
            responder = None
        else:
            responder = user.department.manager
    else:  # 如果不是部门leader, 审批人则为该部门的leader
        responder = user.department.leader
    return responder
