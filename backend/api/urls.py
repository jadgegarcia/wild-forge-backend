from django.urls import path, include, re_path
from .controllers.ActivityController import TeamActivitiesController
from rest_framework_nested import routers
from rest_framework_simplejwt.views import (
    TokenRefreshView,
    TokenVerifyView,
)

from .controllers import *

router = routers.DefaultRouter(trailing_slash=False)
router.register(r'users', UsersController, basename='users')
router.register(r'evals', PeerEvalsController, basename='eval')
router.register(r'classes', ClassRoomsController, basename='class')
router.register(r'activity-templates', ActivityTemplateController, basename='activity-templates')
router.register(r'activity-work-attachments', ActivityWorkAttachmentController, basename='activity-work-attachments')
router.register(r'activity-comments', ActivityCommentController, basename='activity-comments')
router.register(r'activity-criterias', ActivityCriteriaController, basename='activity-criterias')
router.register(r'activity-criteria-settings', ActivityGeminiSettingsController, basename='activity-criteria-settings')
router.register(r'activity-criteria-relations', ActivityCriteriaRelationController, basename='activity-criteria-relations')

classes_router = routers.NestedSimpleRouter(router, r'classes', lookup='class')
classes_router.register(r'members', ClassMembersController, basename='class-members')
classes_router.register(r'teams', TeamsController, basename='class-teams')
classes_router.register(r'activities', ActivityController, basename='class-activities')

team_members = routers.NestedSimpleRouter(classes_router, r'teams', lookup='team')
team_members.register(r'members', TeamMembersController, basename='team-members')
team_members.register(r'activities', TeamActivitiesController, basename='team-activities')


teknoplat_router = routers.DefaultRouter(trailing_slash=False)
teknoplat_router.register('meetings', MeetingsController, basename='meeting')
teknoplat_router.register('pitches', PitchesController, basename='pitches')
teknoplat_router.register('ratings', RatingsController, basename='ratings')
teknoplat_router.register('remarks', RemarksController, basename='remarks')
teknoplat_router.register('idea_validation', ChatbotsController, basename='idea_validation')
teknoplat_router.register('criterias', CriteriasController, basename='criterias')
teknoplat_router.register('meeting_comments', MeetingCommentsController, basename='meeting_comments')

urlpatterns = router.urls
urlpatterns += classes_router.urls
urlpatterns += team_members.urls
urlpatterns += teknoplat_router.urls

urlpatterns += [
    path('tokens/', include([
        path('acquire', TokensController.as_view(), name='acquire_token_pair'),
        path('refresh', TokenRefreshView.as_view(), name='refresh_token'),
        path('verify', TokenVerifyView.as_view(), name='verify_token'),
    ])),
    path('spring/class_team_proj', GetAllClassroomTeamAndProjects.as_view()),
    path('spring/class/<int:class_id>/team_proj',GetTeamsAndProjectsByClassId.as_view()),
    path('spring/team/<int:team_id>/projects', GetProjectsByTeamId.as_view()),
    path('spring/<int:user_id>/projects', UserProjectsView.as_view()),
    path('spring/project', ProjectView.as_view()),
    path('spring/project/<int:project_id>', GetProjectById.as_view()),
    path('spring/project/create', ProjectCreateView.as_view()),
    path('spring/project/<int:project_id>/update', ProjectUpdateView.as_view()),
    path('spring/project/<int:project_id>/delete', DeleteProjectView.as_view()),
    path('spring/project/<int:project_id>/projectboards',GetProjectBoards.as_view()),
    path('spring/projectboards/<int:projectboard_id>',GetProjectBoardById.as_view()),
    path('spring/projectboards/<int:projectboard_id>/versions',GetVersionProjectBoards.as_view()),
    path('spring/project/<int:project_id>/addprojectboards',CreateProjectBoard.as_view()),
    path('spring/projectboards/<int:projectboard_id>/update', UpdateBoard.as_view()),
    path('spring/projectboards/<int:id>/delete', DeleteProjectBoard.as_view()),
    path('spring/template/<int:template_id>', GetTemplate.as_view()),
    path('spring/template/', GetAllTemplate.as_view()),
    path('spring/template/add', CreateTemplate.as_view()),
    path('spring/template/<int:template_id>/update', UpdateTemplate.as_view()),
    path('spring/template/<int:template_id>/delete', DeleteTemplate.as_view())
]