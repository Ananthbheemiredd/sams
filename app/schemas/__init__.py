# # app/schemas/__init__.py
#
# # ========= USER SCHEMAS =========
# from .user_schemas import (
#     UserRegister,
#     UserLogin,
#     TokenResponse,
#     VerifyLoginRequest,
#     LogoutRequest
# )
#
# # ========= MFA SCHEMAS =========
# from .mfa_schema import (
#     MFAEnrollStartOut,
#     MFAEnrollVerifyIn,
#     MFAEnrollVerifyOut,
#     LoginVerifyIn,
# )
#
# # ========= EXAM SCHEMAS =========
# from .exam_schema import (
#     QuestionCreate,
#     QuestionResponse,
#     StudentExamCreate,
#     StudentExamSubmit,
#     StudentExamResponse,
# )
#
#
#
# # ========= OTHER MODULE SCHEMAS =========
# from .admissions_schema import *
# from .application_schema import *
# from .pre_registration_schema import *
# from .calendar_schema import *
# # from .notification_schema import *
# from .fee_schema import *
# from .hostel_schema import *
# from .session_schema import *

from .academic_schema import (
    AssignmentCreate,
    SyllabusCreate,
    TeachingPlanCreate,
)



