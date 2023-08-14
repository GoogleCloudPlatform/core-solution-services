"""
Copyright 2023 Google LLC

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    https://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""

"""References for the Collection"""

from common.models import (
    LearningObject, AssessmentItem, LearningExperience, LearningResource,
    CurriculumPathway, KnowledgeServiceLearningContent, Concept, SubConcept,
    KnowledgeServiceLearningObjective, KnowledgeServiceLearningUnit, Skill,
    SkillServiceCompetency, Category, Domain, SubDomain, Achievement,
    Assessment, SubmittedAssessment, User, UserGroup, Action, Permission,
    Module, Application, Activity, Agent, Rubric,RubricCriterion)

collection_references = {
    # Assessment Service
    "assessment_items": AssessmentItem,
    "assessments": Assessment,
    "submitted_assessments": SubmittedAssessment,
    "rubric_criteria": RubricCriterion,
    "rubrics": Rubric,
    # Learning Object Service
    "learning_resources": LearningResource,
    "learning_objects": LearningObject,
    "learning_experiences": LearningExperience,
    "curriculum_pathways": CurriculumPathway,
    "achievements": Achievement,
    # Knowledge Service
    "learning_resource": KnowledgeServiceLearningContent,
    "concepts": Concept,
    "sub_concepts": SubConcept,
    "learning_objectives": KnowledgeServiceLearningObjective,
    "learning_units": KnowledgeServiceLearningUnit,
    # Skill Service
    "skills": Skill,
    "competencies": SkillServiceCompetency,
    "categories": Category,
    "domains": Domain,
    "sub_domains": SubDomain,
    # User Management
    "user_groups": UserGroup,
    "users": User,
    "actions": Action,
    "action_id": Action,
    "modules": Module,
    "module_id": Module,
    "permissions": Permission,
    "applications": Application,
    "application_id": Application,
    "activities": Activity,
    "agents": Agent
}

LOS_COLLECTIONS = [
    "curriculum_pathways", "learning_experiences", "learning_objects",
    "learning_resources", "assessments"
]

child_parent_dict = {
      "learning_resources": "learning_objects",
      "assessments": "learning_objects",
      "learning_objects": "learning_experiences",
      "learning_experiences": "curriculum_pathways",
      "curriculum_pathways": "curriculum_pathways"
    }
