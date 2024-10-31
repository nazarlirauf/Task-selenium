import os
import time
from kubernetes import client, config
from kubernetes.client import AppsV1Api, CoreV1Api
from kubernetes.client.rest import ApiException

config.load_kube_config()

apps_v1 = AppsV1Api()
core_v1 = CoreV1Api()

docker_image_name = "linuxengineeratl/test-case-controller"

test_case_controller_deployment = {
    "apiVersion": "apps/v1",
    "kind": "Deployment",
    "metadata": {
        "name": "test-case-controller",
        "namespace": "chrome-node"
    },
    "spec": {
        "replicas": 1,
        "selector": {"matchLabels": {"app": "test-case-controller"}},
        "template": {
            "metadata": {"labels": {"app": "test-case-controller"}},
            "spec": {
                "containers": [{
                    "name": "test-case-controller",
                    "image": docker_image_name,
                    "ports": [{"containerPort": 4442}, {"containerPort": 4443}]
                }]
            }
        }
    }
}

# `chrome-node` Deployment yaml konfiqurasiyası
chrome_node_deployment = {
    "apiVersion": "apps/v1",
    "kind": "Deployment",
    "metadata": {
        "name": "chrome-node",
        "namespace": "chrome-node"
    },
    "spec": {
        "replicas": 1,
        "selector": {"matchLabels": {"app": "chrome-node"}},
        "template": {
            "metadata": {"labels": {"app": "chrome-node"}},
            "spec": {
                "containers": [{
                    "name": "chrome-node",
                    "image": "selenium/node-chrome",
                    "env": [
                        {"name": "SE_EVENT_BUS_HOST", "value": "test-case-controller"},
                        {"name": "SE_EVENT_BUS_PUBLISH_PORT", "value": "4442"},
                        {"name": "SE_EVENT_BUS_SUBSCRIBE_PORT", "value": "4443"}
                    ],
                    "ports": [{"containerPort": 4444}]
                }]
            }
        }
    }
}

def build_and_push_docker_image():
    os.system(f"docker build -t {docker_image_name} .")
    print("Docker image built successfully.")

    os.system(f"docker push {docker_image_name}")
    print("Docker image pushed to Docker Hub successfully.")

def deploy_resources():
    try:
        apps_v1.create_namespaced_deployment(namespace="chrome-node", body=test_case_controller_deployment)
        print("test-case-controller deployment created.")
        
        apps_v1.create_namespaced_deployment(namespace="chrome-node", body=chrome_node_deployment)
        print("chrome-node deployment created.")
        
    except ApiException as e:
        print(f"Error deploying resources: {e}")

def check_pods_ready(label_selector, namespace="chrome-node"):
    while True:
        pods = core_v1.list_namespaced_pod(namespace=namespace, label_selector=label_selector).items
        if all(pod.status.phase == "Running" for pod in pods):
            print(f"All pods with label {label_selector} are running.")
            break
        else:
            print(f"Waiting for pods with label {label_selector} to be ready...")
            time.sleep(5)

def run_selenium_tests():
    os.system("kubectl exec -n chrome-node $(kubectl get pod -n chrome-node -l app=test-case-controller -o jsonpath='{.items[0].metadata.name}') -- python /app/test_script.py")

if __name__ == "__main__":
    build_and_push_docker_image()
    deploy_resources()
    check_pods_ready("app=test-case-controller")
    check_pods_ready("app=chrome-node")
    run_selenium_tests()
