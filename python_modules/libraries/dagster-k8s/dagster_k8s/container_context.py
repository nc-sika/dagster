from typing import TYPE_CHECKING, Any, Dict, List, NamedTuple, Optional

from dagster import check
from dagster.config.validate import process_config
from dagster.core.errors import DagsterInvalidConfigError
from dagster.core.storage.pipeline_run import PipelineRun
from dagster.utils import merge_dicts

if TYPE_CHECKING:
    from . import K8sRunLauncher

from .job import DagsterK8sJobConfig


class K8sContainerContext(
    NamedTuple(
        "_K8sContainerContext",
        [
            ("image_pull_policy", Optional[str]),
            ("image_pull_secrets", List[Dict[str, str]]),
            ("service_account_name", Optional[str]),
            ("env_config_maps", List[str]),
            ("env_secrets", List[str]),
            ("env_vars", List[str]),
            ("volume_mounts", List[Dict[str, Any]]),
            ("volumes", List[Dict[str, Any]]),
            ("labels", Dict[str, str]),
            ("namespace", Optional[str]),
        ],
    )
):
    """Encapsulates configuration that can be applied to a K8s job running Dagster code.
    Can be persisted on a PipelineRun at run submission time based on metadata from the
    code location and then included in the job's configuration at run launch time or step
    launch time."""

    def __new__(
        cls,
        image_pull_policy: Optional[str] = None,
        image_pull_secrets: Optional[List[Dict[str, str]]] = None,
        service_account_name: Optional[str] = None,
        env_config_maps: Optional[List[str]] = None,
        env_secrets: Optional[List[str]] = None,
        env_vars: Optional[List[str]] = None,
        volume_mounts: Optional[List[Dict[str, Any]]] = None,
        volumes: Optional[List[Dict[str, Any]]] = None,
        labels: Optional[Dict[str, str]] = None,
        namespace: Optional[str] = None,
    ):
        return super(K8sContainerContext, cls).__new__(
            cls,
            image_pull_policy=check.opt_str_param(image_pull_policy, "image_pull_policy"),
            image_pull_secrets=check.opt_list_param(image_pull_secrets, "image_pull_secrets"),
            service_account_name=check.opt_str_param(service_account_name, "service_account_name"),
            env_config_maps=check.opt_list_param(env_config_maps, "env_config_maps"),
            env_secrets=check.opt_list_param(env_secrets, "env_secrets"),
            env_vars=check.opt_list_param(env_vars, "env_vars"),
            volume_mounts=check.opt_list_param(volume_mounts, "volume_mounts"),
            volumes=check.opt_list_param(volumes, "volumes"),
            labels=check.opt_dict_param(labels, "labels"),
            namespace=check.opt_str_param(namespace, "namespace"),
        )

    def merge(self, other: "K8sContainerContext") -> "K8sContainerContext":
        return K8sContainerContext(
            image_pull_policy=(
                other.image_pull_policy if other.image_pull_policy else self.image_pull_policy
            ),
            image_pull_secrets=other.image_pull_secrets + self.image_pull_secrets,
            service_account_name=(
                other.service_account_name
                if other.service_account_name
                else self.service_account_name
            ),
            env_config_maps=other.env_config_maps + self.env_config_maps,
            env_secrets=other.env_secrets + self.env_secrets,
            env_vars=other.env_vars + self.env_vars,
            volume_mounts=other.volume_mounts + self.volume_mounts,
            volumes=other.volumes + self.volumes,
            labels=merge_dicts(other.labels, self.labels),
            namespace=other.namespace if other.namespace else self.namespace,
        )

    @staticmethod
    def create_for_run(pipeline_run: PipelineRun, run_launcher: Optional["K8sRunLauncher"]):
        context = K8sContainerContext()

        if run_launcher:
            context = context.merge(
                K8sContainerContext(
                    image_pull_policy=run_launcher.image_pull_policy,
                    image_pull_secrets=run_launcher.image_pull_secrets,
                    service_account_name=run_launcher.service_account_name,
                    env_config_maps=run_launcher.env_config_maps,
                    env_secrets=run_launcher.env_secrets,
                    env_vars=run_launcher.env_vars,
                    volume_mounts=run_launcher.volume_mounts,
                    volumes=run_launcher.volumes,
                    labels=run_launcher.labels,
                    namespace=run_launcher.job_namespace,
                )
            )

        run_container_context = (
            pipeline_run.pipeline_code_origin.repository_origin.container_context
            if pipeline_run.pipeline_code_origin
            else None
        )

        if not run_container_context:
            return context

        return context.merge(K8sContainerContext.create_from_config(run_container_context))

    @staticmethod
    def create_from_config(run_container_context):
        run_k8s_container_context = (
            run_container_context.get("k8s", {}) if run_container_context else {}
        )

        if not run_k8s_container_context:
            return K8sContainerContext()

        processed_container_context = process_config(
            DagsterK8sJobConfig.config_type_container_context(), run_k8s_container_context
        )

        if not processed_container_context.success:
            raise DagsterInvalidConfigError(
                "Errors while parsing k8s container context",
                processed_container_context.errors,
                run_k8s_container_context,
            )

        processed_context_value = processed_container_context.value

        return K8sContainerContext(
            image_pull_policy=processed_context_value.get("image_pull_policy"),
            image_pull_secrets=processed_context_value.get("image_pull_secrets"),
            service_account_name=processed_context_value.get("service_account_name"),
            env_config_maps=processed_context_value.get("env_config_maps"),
            env_secrets=processed_context_value.get("env_secrets"),
            env_vars=processed_context_value.get("env_vars"),
            volume_mounts=processed_context_value.get("volume_mounts"),
            volumes=processed_context_value.get("volumes"),
            labels=processed_context_value.get("labels"),
            namespace=processed_context_value.get("namespace"),
        )

    def get_k8s_job_config(self, job_image, run_launcher):
        return DagsterK8sJobConfig(
            job_image=job_image if job_image else run_launcher.job_image,
            dagster_home=run_launcher.dagster_home,
            image_pull_policy=self.image_pull_policy,
            image_pull_secrets=self.image_pull_secrets,
            service_account_name=self.service_account_name,
            instance_config_map=run_launcher.instance_config_map,
            postgres_password_secret=run_launcher.postgres_password_secret,
            env_config_maps=self.env_config_maps,
            env_secrets=self.env_secrets,
            env_vars=self.env_vars,
            volume_mounts=self.volume_mounts,
            volumes=self.volumes,
            labels=self.labels,
        )
