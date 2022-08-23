
from e2e.utils.utils import print_banner
import argparse
from e2e.utils.utils import kubectl_delete, kubectl_delete_crd, uninstall_helm, delete_kustomize, load_yaml_file
import os
import subprocess


INSTALLATION_PATH_FILE = "./resources/kubeflow_installation_paths.yaml"
path_dic = load_yaml_file(INSTALLATION_PATH_FILE)

def uninstall_kubeflow(installation_option,aws_telemetry_option,deployment_option):
    INSTALLATION_OPTION = installation_option
    AWS_TELEMETRY_OPTION = aws_telemetry_option
    DEPLOYMENT_OPTION = deployment_option
    print_banner(f"You are uninstalling kubeflow {DEPLOYMENT_OPTION} deployment with {INSTALLATION_OPTION}")

    
    if DEPLOYMENT_OPTION == 'cognito':
        subprocess.call(f"kubectl delete profiles --all".split())
        delete_component("aws-authservice", path_dic["aws_authservice"]["helm"], path_dic["aws_authservice"]["kustomize"], installation_option=INSTALLATION_OPTION)
        delete_component("ingress", path_dic["ingress"]["helm"], path_dic["ingress"]["kustomize"], installation_option=INSTALLATION_OPTION)
        delete_component("alb-controller", path_dic["alb_controller"]["helm"], path_dic["alb_controller"]["kustomize"], namespace='kube-system', installation_option=INSTALLATION_OPTION)
        
    if DEPLOYMENT_OPTION != 'cognito':
        delete_component("user-namespace",path_dic["user_namespace"]["helm"], path_dic["user_namespace"]["kustomize"], installation_option = INSTALLATION_OPTION)
    delete_component("profiles-and-kfam",path_dic["profiles_and_kfam"]["helm"], path_dic["profiles_and_kfam"]["kustomize"], installation_option = INSTALLATION_OPTION)
    delete_component("tensorboard-controller",path_dic["tensorboard_controller"]["helm"], path_dic["tensorboard_controller"]["kustomize"], installation_option = INSTALLATION_OPTION)
    delete_component("tensorboards-web-app",path_dic["tensorboards_web_app"]["helm"], path_dic["tensorboards_web_app"]["kustomize"], installation_option = INSTALLATION_OPTION)
    
    #katib
    if DEPLOYMENT_OPTION == 'rds-and-s3' or DEPLOYMENT_OPTION == 'rds-only':
        delete_component("katib",path_dic["katib_external_db"]["helm"],path_dic["katib_external_db"]["kustomize"], installation_option = INSTALLATION_OPTION)
    else:
        delete_component("katib",path_dic["katib"]["helm"],path_dic["katib"]["kustomize"], installation_option = INSTALLATION_OPTION)
    
    delete_component("training-operator",path_dic["training_operator"]["helm"],path_dic["training_operator"]["kustomize"], installation_option = INSTALLATION_OPTION)
    delete_component("volumes-web-app",path_dic["volumes_web_app"]["helm"],path_dic["volumes_web_app"]["kustomize"], installation_option = INSTALLATION_OPTION)
    delete_component("notebook-controller",path_dic["notebook_controller"]["helm"],path_dic["notebook_controller"]["kustomize"], installation_option = INSTALLATION_OPTION)
    delete_component("jupyter-web-app",path_dic["jupyter_web_app"]["helm"],path_dic["jupyter_web_app"]["kustomize"], installation_option = INSTALLATION_OPTION)
    delete_component("admission-webhook",path_dic["admission_webhook"]["helm"],path_dic["admission_webhook"]["kustomize"], installation_option = INSTALLATION_OPTION)
    
    #kubeflow-pipelines
    if DEPLOYMENT_OPTION == 'rds-and-s3':
        delete_component("kubeflow-pipelines",path_dic["kubeflow_pipelines_rds_and_s3"]["helm"], path_dic["kubeflow_pipelines_rds_and_s3"]["kustomize"], installation_option = INSTALLATION_OPTION)
    elif DEPLOYMENT_OPTION == 'rds-only':
        delete_component("kubeflow-pipelines",path_dic["kubeflow_pipelines_rds_only"]["helm"], path_dic["kubeflow_pipelines_rds_only"]["kustomize"], installation_option = INSTALLATION_OPTION)
    elif DEPLOYMENT_OPTION == 's3-only':
        delete_component("kubeflow-pipelines",path_dic["kubeflow_pipelines_s3_only"]["helm"], path_dic["kubeflow_pipelines_s3_only"]["kustomize"], installation_option = INSTALLATION_OPTION)
    else:
        delete_component("kubeflow-pipelines",path_dic["kubeflow_pipelines"]["helm"], path_dic["kubeflow_pipelines"]["kustomize"], installation_option = INSTALLATION_OPTION)

    delete_component("central-dashboard",path_dic["central_dashboard"]["helm"],path_dic["central_dashboard"]["kustomize"], installation_option = INSTALLATION_OPTION)
    delete_component("models-web-app",path_dic["models_web_app"]["helm"],path_dic["models_web_app"]["kustomize"], installation_option = INSTALLATION_OPTION)
    delete_component("kserve",path_dic["kserve"]["helm"],path_dic["kserve"]["kustomize"], installation_option = INSTALLATION_OPTION)
    delete_component("kubeflow-istio-resources",path_dic["kubeflow_istio_resources"]["helm"],path_dic["kubeflow_istio_resources"]["kustomize"], installation_option = INSTALLATION_OPTION)
    if DEPLOYMENT_OPTION != 'cognito':
        delete_component("oidc-authservice",path_dic["oidc_authservice"]["helm"],path_dic["oidc_authservice"]["kustomize"], installation_option = INSTALLATION_OPTION)
    delete_component("knative-eventing",path_dic["knative_eventing"]["helm"],path_dic["knative_eventing"]["kustomize"], installation_option = INSTALLATION_OPTION)
    delete_component("knative-serving",path_dic["knative_serving"]["helm"],path_dic["knative_serving"]["kustomize"], installation_option = INSTALLATION_OPTION)
    delete_component("cluster-local-gateway",path_dic["cluster_local_gateway"]["helm"],path_dic["cluster_local_gateway"]["kustomize"], installation_option = INSTALLATION_OPTION)
    if DEPLOYMENT_OPTION != 'cognito':
        delete_component("dex",path_dic["dex"]["helm"],path_dic["dex"]["kustomize"], installation_option = INSTALLATION_OPTION)
    delete_component("kubeflow-namespace", path_dic["kubeflow_namespace"]["helm"], path_dic["kubeflow_namespace"]["kustomize"], installation_option = INSTALLATION_OPTION)

    

    if INSTALLATION_OPTION == "helm":
        delete_component("istio-1-14",path_dic["istio"]["helm"], installation_option = INSTALLATION_OPTION)
        
    else:
        print(f"==========uninstallating Istio-1-14...==========")
        #delete_component("Istio-base",kustomize_path=path_dic["istio_base"]["kustomize"], installation_option = INSTALLATION_OPTION)
        delete_component("Istio-namespace",kustomize_path=path_dic["istio_namespace"]["kustomize"], installation_option = INSTALLATION_OPTION)
        delete_component("Istio-crd",kustomize_path=path_dic["istio_crd"]["kustomize"], installation_option = INSTALLATION_OPTION)
    

    delete_component("kubeflow-issuer",path_dic["kubeflow_issuer"]["helm"],path_dic["kubeflow_issuer"]["kustomize"], installation_option = INSTALLATION_OPTION)
    delete_component("kubeflow-roles",path_dic["kubeflow_roles"]["helm"], path_dic["kubeflow_roles"]["kustomize"], installation_option = INSTALLATION_OPTION)
    delete_component("cert-manager",path_dic["cert_manager"]["helm"], path_dic["cert_manager"]["kustomize"], namespace="cert-manager", installation_option = INSTALLATION_OPTION)
    if AWS_TELEMETRY_OPTION == "enable":
        delete_component("aws-telemetry",path_dic["aws_telemetry"]["helm"],path_dic["aws_telemetry"]["kustomize"], installation_option = INSTALLATION_OPTION)
    
def delete_component(chart_name=None, chart_path=None, kustomize_path=None, namespace=None, installation_option = 'kustomize'):
    print(f"==========uninstallating {chart_name}...==========")
    if installation_option == 'helm':
        uninstall_helm(chart_name,namespace)
        if os.path.isdir(f"{chart_path}/crds"):
            print(f"deleting {chart_name} crds ...")
            kubectl_delete(f"{chart_path}/crds")
            #clear up implicit crd resources for Dex
    
    else:
        delete_kustomize(kustomize_path)
    
    if chart_name == "dex" or kustomize_path == path_dic["dex"]["kustomize"]:
                kubectl_delete_crd("authrequests.dex.coreos.com")
                kubectl_delete_crd("connectors.dex.coreos.com")
                kubectl_delete_crd("devicerequests.dex.coreos.com")
                kubectl_delete_crd("devicetokens.dex.coreos.com")
                kubectl_delete_crd("oauth2clients.dex.coreos.com")
                kubectl_delete_crd("offlinesessionses.dex.coreos.com")
                kubectl_delete_crd("passwords.dex.coreos.com")
                kubectl_delete_crd("refreshtokens.dex.coreos.com")
                kubectl_delete_crd("signingkeies.dex.coreos.com")
        

    print(f"All {chart_name} resources are cleared!")






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
        help=f"Kubeflow deployment options (vanilla/cognito/rds-s3/rds-only/s3-only/cognito-rds-s3), default is set to {DEPLOYMENT_OPTION_DEFAULT}",
        required=False,
    )

    args, _ = parser.parse_known_args()
    INSTALLATION_OPTION=args.installation_option
    AWS_TELEMETRY_OPTION=args.aws_telemetry_option
    DEPLOYMENT_OPTION=args.deployment_option
    uninstall_kubeflow(INSTALLATION_OPTION, AWS_TELEMETRY_OPTION, DEPLOYMENT_OPTION)