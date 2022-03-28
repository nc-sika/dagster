# pylint: disable=redefined-outer-name

import pytest
from dagster_k8s.container_context import K8sContainerContext

from dagster.core.errors import DagsterInvalidConfigError


@pytest.fixture
def container_context_config():
    return {
        "k8s": {
            "image_pull_policy": "Always",
            "image_pull_secrets": [{"name": "my_secret"}],
            "service_account_name": "my_service_account",
            "env_config_maps": ["my_config_map"],
            "env_secrets": ["my_secret"],
            "env_vars": ["MY_ENV_VAR"],
            "volume_mounts": [
                {
                    "mountPath": "my_mount_path",
                    "mountPropagation": "my_mount_propagation",
                    "name": "a_volume_mount_one",
                    "readOnly": False,
                    "subPath": "path/",
                }
            ],
            "volumes": [{"name": "foo", "configMap": {"name": "settings-cm"}}],
            "labels": {"foo_label": "bar_value"},
            "namespace": "my_namespace",
        }
    }


@pytest.fixture
def other_container_context_config():
    return {
        "k8s": {
            "image_pull_policy": "Never",
            "image_pull_secrets": [{"name": "your_secret"}],
            "service_account_name": "your_service_account",
            "env_config_maps": ["your_config_map"],
            "env_secrets": ["your_secret"],
            "env_vars": ["YOUR_ENV_VAR"],
            "volume_mounts": [
                {
                    "mountPath": "your_mount_path",
                    "mountPropagation": "your_mount_propagation",
                    "name": "b_volume_mount_one",
                    "readOnly": True,
                    "subPath": "your_path/",
                }
            ],
            "volumes": [{"name": "bar", "configMap": {"name": "your-settings-cm"}}],
            "labels": {"bar_label": "baz_value"},
            "namespace": "your_namespace",
        }
    }


@pytest.fixture(name="empty_container_context")
def empty_container_context_fixture():
    return K8sContainerContext()


@pytest.fixture(name="container_context")
def container_context_fixture(container_context_config):
    return K8sContainerContext.create_from_config(container_context_config)


@pytest.fixture(name="other_container_context")
def other_container_context_fixture(other_container_context_config):
    return K8sContainerContext.create_from_config(other_container_context_config)


def test_empty_container_context(empty_container_context):
    assert empty_container_context.image_pull_policy == None
    assert empty_container_context.image_pull_secrets == []
    assert empty_container_context.service_account_name == None
    assert empty_container_context.env_config_maps == []
    assert empty_container_context.env_secrets == []
    assert empty_container_context.env_vars == []
    assert empty_container_context.volume_mounts == []
    assert empty_container_context.volumes == []
    assert empty_container_context.labels == {}
    assert empty_container_context.namespace == None


def test_invalid_config():
    with pytest.raises(
        DagsterInvalidConfigError, match="Errors while parsing k8s container context"
    ):
        K8sContainerContext.create_from_config(
            {"k8s": {"image_push_policy": {"foo": "bar"}}}
        )  # invalid formatting


def test_merge(empty_container_context, container_context, other_container_context):
    assert container_context.image_pull_policy == "Always"
    assert container_context.image_pull_secrets == [{"name": "my_secret"}]
    assert container_context.service_account_name == "my_service_account"
    assert container_context.env_config_maps == ["my_config_map"]
    assert container_context.env_secrets == ["my_secret"]
    assert container_context.env_vars == ["MY_ENV_VAR"]
    assert container_context.volume_mounts == [
        {
            "mountPath": "my_mount_path",
            "mountPropagation": "my_mount_propagation",
            "name": "a_volume_mount_one",
            "readOnly": False,
            "subPath": "path/",
        }
    ]
    assert container_context.volumes == [{"name": "foo", "configMap": {"name": "settings-cm"}}]
    assert container_context.labels == {"foo_label": "bar_value"}
    assert container_context.namespace == "my_namespace"

    merged = container_context.merge(other_container_context)

    assert merged.image_pull_policy == "Never"
    assert merged.image_pull_secrets == [
        {"name": "your_secret"},
        {"name": "my_secret"},
    ]
    assert merged.service_account_name == "your_service_account"
    assert merged.env_config_maps == [
        "your_config_map",
        "my_config_map",
    ]
    assert merged.env_secrets == [
        "your_secret",
        "my_secret",
    ]
    assert merged.env_vars == [
        "YOUR_ENV_VAR",
        "MY_ENV_VAR",
    ]
    assert merged.volume_mounts == [
        {
            "mountPath": "your_mount_path",
            "mountPropagation": "your_mount_propagation",
            "name": "b_volume_mount_one",
            "readOnly": True,
            "subPath": "your_path/",
        },
        {
            "mountPath": "my_mount_path",
            "mountPropagation": "my_mount_propagation",
            "name": "a_volume_mount_one",
            "readOnly": False,
            "subPath": "path/",
        },
    ]
    assert merged.volumes == [
        {"name": "bar", "configMap": {"name": "your-settings-cm"}},
        {"name": "foo", "configMap": {"name": "settings-cm"}},
    ]
    assert merged.labels == {"foo_label": "bar_value", "bar_label": "baz_value"}
    assert merged.namespace == "your_namespace"

    assert container_context.merge(empty_container_context) == container_context
    assert empty_container_context.merge(container_context) == container_context
