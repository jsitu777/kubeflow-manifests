
from pickle import FALSE
from e2e.utils.utils import load_yaml_file, print_banner
import argparse
from e2e.utils.utils import kubectl_apply, kubectl_wait_pods, kubectl_get_cronjob, kubectl_wait_crd,kubectl_get_namespace, apply_kustomize, install_helm
import subprocess
import time

INSTALLATION_PATH_FILE = "./resources/installation_config/kubeflow_installation_paths.yaml"
path_dic = load_yaml_file(INSTALLATION_PATH_FILE)

def install_kubeflow(installation_option,aws_telemetry_option,deployment_option):
    
    INSTALLATION_OPTION = installation_option
    AWS_TELEMETRY_OPTION = aws_telemetry_option
    DEPLOYMENT_OPTION = deployment_option
    print_banner(f"You are installing kubeflow {DEPLOYMENT_OPTION} deployment with {INSTALLATION_OPTION}")
    """
    #install cert-manager
    build_component(INSTALLATION_OPTION,
                    DEPLOYMENT_OPTION,
                    "cert-manager",
                    namespace='cert-manager',
                    identifier='app.kubernetes.io/instance',
                    common_label='cert-manager',
                    )
    #install kubeflow-issuer
    build_component(INSTALLATION_OPTION,
                    DEPLOYMENT_OPTION,
                    "kubeflow-issuer",
                    validation_needed=False)
    build_component(INSTALLATION_OPTION,
                    DEPLOYMENT_OPTION,
                    "kubeflow-roles",
                    validation_needed=False)
    
    #install istio
    build_component(INSTALLATION_OPTION,
                    DEPLOYMENT_OPTION,
                    "istio-1-14",
                    namespace='istio-system',
                    common_label='istio-ingressgateway, istiod'
                    )
    #install dex
    build_component(INSTALLATION_OPTION,
                    DEPLOYMENT_OPTION,
                    "dex",
                    namespace="auth",
                    common_label="dex"
                    )
    #install kubeflow-namespace
    build_component(INSTALLATION_OPTION,
                    DEPLOYMENT_OPTION,
                    "kubeflow-namespace",
                    validation_needed=False)
    
    #install cluster-local-gateway
    build_component(INSTALLATION_OPTION,
                    DEPLOYMENT_OPTION,
                    "cluster-local-gateway",
                    namespace='istio-system',
                    common_label='cluster-local-gateway')
    
    #install knative-serving
    build_component(INSTALLATION_OPTION,
                    DEPLOYMENT_OPTION,
                    "knative-serving",
                    namespace="knative-serving",
                    identifier="app.kubernetes.io/name",
                    common_label="knative-serving",
                    crd_required='images.caching.internal.knative.dev')
    
    #install knative eventing
    build_component(INSTALLATION_OPTION,
                    DEPLOYMENT_OPTION,
                    "knative-eventing",
                    namespace="knative-eventing",
                    identifier="app.kubernetes.io/name",
                    common_label="knative-eventing"
                    )
    
    #install oidc-authservice
    build_component(INSTALLATION_OPTION,
                    DEPLOYMENT_OPTION,
                    "oidc-authservice",
                    namespace="istio-system",
                    common_label='authservice'
                    )

    #install kubeflow-istio-resources
    build_component(INSTALLATION_OPTION,
                    DEPLOYMENT_OPTION,
                    "kubeflow-istio-resources",
                    validation_needed=False)
    
    #install kserve
    build_component(INSTALLATION_OPTION,
                    DEPLOYMENT_OPTION,
                    "kserve",
                    namespace="kubeflow",
                    crd_required="clusterservingruntimes.serving.kserve.io",
                    common_label='kserve'
                    )
    

    #install secrets-manager
    build_component(INSTALLATION_OPTION,
                    DEPLOYMENT_OPTION,
                    "aws-secrets-manager",
                    namespace='kubeflow',
                    common_label='aws-secrets-sync')

    #install models-web-app
    build_component(INSTALLATION_OPTION,
                    DEPLOYMENT_OPTION,
                    "models-web-app",
                    namespace="kubeflow",
                    identifier="kustomize.component",
                    common_label="kserve-models-web-app")
    
    #build central-dashboard
    build_component(INSTALLATION_OPTION,
                    DEPLOYMENT_OPTION,
                    "central-dashboard",
                    namespace="kubeflow",
                    common_label="centraldashboard")

    #build kubeflow-pipelines
    build_component(INSTALLATION_OPTION,
                    DEPLOYMENT_OPTION,
                    "kubeflow-pipelines",
                    namespace="kubeflow",
                    crd_required="compositecontrollers.metacontroller.k8s.io",
                    common_label='kubeflow-pipelines',
                    identifier='application-crd-id',
                    timeout=240
                    )
 
    #build admission-webhook
    build_component(INSTALLATION_OPTION,
                    DEPLOYMENT_OPTION,
                    "admission-webhook",
                    namespace="kubeflow",
                    common_label="poddefaults")
    #build notebook-controller
    build_component(INSTALLATION_OPTION,
                    DEPLOYMENT_OPTION,
                    "notebook-controller",
                    namespace="kubeflow",
                    common_label='notebook-controller')

    #build jupyter-web-app
    build_component(INSTALLATION_OPTION,
                    DEPLOYMENT_OPTION,
                    "jupyter-web-app",
                    namespace="kubeflow",
                    common_label='jupyter-web-app')
    
    #build volumes-web-app
    build_component(INSTALLATION_OPTION,
                    DEPLOYMENT_OPTION,
                    "volumes-web-app",
                    namespace="kubeflow",
                    common_label='volumes-web-app')
    
    #build katib  
    build_component(INSTALLATION_OPTION,
                    DEPLOYMENT_OPTION,
                    "katib",
                    namespace="kubeflow",
                    common_label='controller, db-manager, ui',
                    identifier="katib.kubeflow.org/component",
                    timeout=240)

    
    #build training operator
    build_component(INSTALLATION_OPTION,
                    DEPLOYMENT_OPTION,
                    "training-operator",
                    namespace="kubeflow",
                    common_label='kubeflow-training-operator',
                    identifier='control-plane')
    #build tensorboard-controller
    build_component(INSTALLATION_OPTION,
                    DEPLOYMENT_OPTION,
                    "tensorboard-controller",
                    namespace="kubeflow",
                    common_label='tensorboard-controller')
    #build tensorboard-web-app
    build_component(INSTALLATION_OPTION,
                    DEPLOYMENT_OPTION,
                    "tensorboards-web-app",
                    namespace="kubeflow",
                    common_label="tensorboards-web-app")
    
    #build profile manager
    build_component(INSTALLATION_OPTION,
                    DEPLOYMENT_OPTION,
                    "profiles-and-kfam",
                    namespace="kubeflow",
                    common_label="profiles",
                    identifier="kustomize.component")
    """
    #build user-namespace
    build_component(INSTALLATION_OPTION,
                    DEPLOYMENT_OPTION,
                    "user-namespace",
                    validation_needed=False)

    #build Ingress
    build_component(INSTALLATION_OPTION,
                    DEPLOYMENT_OPTION,
                    "ingress",
                    validation_needed=False)
    
    #build alb-controller
    build_component(INSTALLATION_OPTION,
                    DEPLOYMENT_OPTION,
                    "alb-controller",
                    common_label='aws-load-balancer-controller',
                    identifier='app.kubernetes.io/name',
                    namespace='kube-system')

    #build aws-authservice
    build_component(INSTALLATION_OPTION,
                    DEPLOYMENT_OPTION,
                    "aws-authservice",
                    common_label='aws-authservice',
                    namespace='istio-system')

    if AWS_TELEMETRY_OPTION == "enable":
        build_component(INSTALLATION_OPTION,
                        DEPLOYMENT_OPTION,
                        "aws-telemetry",
                        validation_needed=False)

def build_component(INSTALLATION_OPTION, 
                    DEPLOYMENT_OPTION, 
                    component_name,
                    validation_needed=True, 
                    identifier='app', 
                    namespace=None,
                    crd_required=None,
                    common_label=None,
                    timeout=120,
                    condition='ready'
                    ):
    print(f"==========Installing {component_name}==========")
    if path_dic[component_name][INSTALLATION_OPTION][DEPLOYMENT_OPTION] == None:
        print (f"component {component_name} is not applicable for deployment option: {DEPLOYMENT_OPTION}")
        return
    else:
        installation_path = path_dic[component_name][INSTALLATION_OPTION][DEPLOYMENT_OPTION]
        if INSTALLATION_OPTION == "helm":
            install_helm(component_name, installation_path, namespace)
        #kustomize
        else:
            if isinstance(installation_path, list):
                #dealing with istio
                for kustomize_path in installation_path:    
                    if crd_required:
                        apply_kustomize(kustomize_path, crd_required)
                    apply_kustomize(kustomize_path)
            else:
                apply_kustomize(installation_path)
        
    if validation_needed:
        print(f"Waiting for {component_name} pods to be ready ...")
        retcode = kubectl_wait_pods(common_label, namespace, timeout,condition,identifier)
        assert retcode == 0
    print(f"All {component_name} pods are running!")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    INSTALLATION_OPTION_DEFAULT="kustomize"
    parser.add_argument(
        "--installation_option",
        type=str,
        default=INSTALLATION_OPTION_DEFAULT,
        help=f"Kubeflow Installation option (helm/kustomize), default is set to {INSTALLATION_OPTION_DEFAULT}",
        required=False,
    )
    AWS_TELEMETRY_DEFAULT="enable"
    parser.add_argument(
        "--aws_telemetry_option",
        type=str,
        default=AWS_TELEMETRY_DEFAULT,
        help=f"Usage tracking (enable/disable), default is set to {AWS_TELEMETRY_DEFAULT}",
        required=False,
    )
    DEPLOYMENT_OPTION_DEFAULT="vanilla"
    parser.add_argument(
        "--deployment_option",
        type=str,
        default=DEPLOYMENT_OPTION_DEFAULT,
        help=f"Kubeflow deployment options (vanilla/cognito/rds_and_s3/rds_only/s3_only/cognito-rds-s3), default is set to {DEPLOYMENT_OPTION_DEFAULT}",
        required=False,
    )

    args, _ = parser.parse_known_args()
    INSTALLATION_OPTION=args.installation_option
    AWS_TELEMETRY_OPTION=args.aws_telemetry_option
    DEPLOYMENT_OPTION=args.deployment_option
    install_kubeflow(INSTALLATION_OPTION,AWS_TELEMETRY_OPTION,DEPLOYMENT_OPTION)