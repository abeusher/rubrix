from typing import Type

from fastapi import APIRouter, Body, Depends, Security

from rubrix.server.apis.v0.models.commons.model import TaskType
from rubrix.server.apis.v0.models.commons.params import DATASET_NAME_PATH_PARAM
from rubrix.server.apis.v0.models.commons.workspace import CommonTaskQueryParams
from rubrix.server.apis.v0.models.dataset_settings import TextClassificationSettings
from rubrix.server.security import auth
from rubrix.server.security.model import User
from rubrix.server.services.datasets import DatasetsService, SVCDatasetSettings


def configure_router(router: APIRouter):

    task = TaskType.text_classification
    base_endpoint = f"/{task}/{{name}}/settings"
    svc_settings_class: Type[SVCDatasetSettings] = type(
        f"{task}_DatasetSettings", (SVCDatasetSettings, TextClassificationSettings), {}
    )

    @router.get(
        path=base_endpoint,
        name=f"get_dataset_settings_for_{task}",
        operation_id=f"get_dataset_settings_for_{task}",
        description=f"Get the {task} dataset settings",
        response_model_exclude_none=True,
        response_model=TextClassificationSettings,
    )
    async def get_dataset_settings(
        name: str = DATASET_NAME_PATH_PARAM,
        ws_params: CommonTaskQueryParams = Depends(),
        datasets: DatasetsService = Depends(DatasetsService.get_instance),
        user: User = Security(auth.get_user, scopes=["read:dataset.settings"]),
    ) -> TextClassificationSettings:

        found_ds = datasets.find_by_name(
            user=user,
            name=name,
            workspace=ws_params.workspace,
            task=task,
        )

        settings = await datasets.get_settings(
            user=user, dataset=found_ds, class_type=svc_settings_class
        )
        return TextClassificationSettings.parse_obj(settings)

    @router.put(
        path=base_endpoint,
        name=f"save_dataset_settings_for_{task}",
        operation_id=f"save_dataset_settings_for_{task}",
        description=f"Save the {task} dataset settings",
        response_model_exclude_none=True,
        response_model=TextClassificationSettings,
    )
    async def save_settings(
        request: TextClassificationSettings = Body(
            ..., description=f"The {task} dataset settings"
        ),
        name: str = DATASET_NAME_PATH_PARAM,
        ws_params: CommonTaskQueryParams = Depends(),
        datasets: DatasetsService = Depends(DatasetsService.get_instance),
        user: User = Security(auth.get_user, scopes=["write:dataset.settings"]),
    ) -> TextClassificationSettings:

        found_ds = datasets.find_by_name(
            user=user,
            name=name,
            task=task,
            workspace=ws_params.workspace,
        )
        # TODO(frascuchon): validate settings...
        settings = await datasets.save_settings(
            user=user,
            dataset=found_ds,
            settings=svc_settings_class.parse_obj(request.dict()),
        )
        return TextClassificationSettings.parse_obj(settings)

    @router.delete(
        path=base_endpoint,
        operation_id=f"delete_{task}_settings",
        name=f"delete_{task}_settings",
        description=f"Delete {task} dataset settings",
    )
    async def delete_settings(
        name: str = DATASET_NAME_PATH_PARAM,
        ws_params: CommonTaskQueryParams = Depends(),
        datasets: DatasetsService = Depends(DatasetsService.get_instance),
        user: User = Security(auth.get_user, scopes=["delete:dataset.settings"]),
    ) -> None:
        found_ds = datasets.find_by_name(
            user=user,
            name=name,
            task=task,
            workspace=ws_params.workspace,
        )
        await datasets.delete_settings(
            user=user,
            dataset=found_ds,
        )

    return router