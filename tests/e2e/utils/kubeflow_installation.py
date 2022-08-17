
from e2e.utils.utils import load_yaml_file, print_banner
import argparse
from e2e.utils.utils import kubectl_apply, kubectl_wait_pods, kubectl_get_cronjob, kubectl_wait_crd,kubectl_get_namespace, apply_kustomize, install_helm
import subprocess
import time

INSTALLATION_PATH_FILE = "./resources/kubeflow_installation_paths.yaml"
path_dic = load_yaml_file(INSTALLATION_PATH_FILE)

def install_kubeflow(installation_option,aws_telemetry_option):
    #print_banner(f"You are installing kubeflow with {args.installation_option}")
    INSTALLATION_OPTION = installation_option
    AWS_TELEMETRY_OPTION = aws_telemetry_option
    build_certManager(INSTALLATION_OPTION)
    
    if INSTALLATION_OPTION == "helm":
        print("==========Installing Kubeflow-Roles==========")
        install_helm("kubeflow-roles", path_dic["kubeflow_roles"]["helm"])
        print("==========Installing Kubeflow-Issuer==========")
        install_helm("kubeflow-issuer", path_dic["kubeflow_issuer"]["helm"])
    else:
        print("==========Installing Kubeflow-Roles==========")
        apply_kustomize(path_dic["kubeflow_roles"]["kustomize"])
        print("==========Installing Kubeflow-Issuer==========")
        apply_kustomize(path_dic["kubeflow_issuer"]["kustomize"])
   
    build_istio(INSTALLATION_OPTION)
    build_dex(INSTALLATION_OPTION)
    
    print("==========Installing Kubeflow-Namespace==========")
    
    if INSTALLATION_OPTION == "helm":
        install_helm("kubeflow-namespace", path_dic["kubeflow_namespace"]["helm"])
    else:
        apply_kustomize(path_dic["kubeflow_namespace"]["kustomize"])
    

    build_clusterLocalGateway(INSTALLATION_OPTION)
    build_knativeServing(INSTALLATION_OPTION)
    build_knativeEventing(INSTALLATION_OPTION)
    build_oidcAuthService(INSTALLATION_OPTION)
    print("==========Installing Kubeflow-Istio-Resources==========")
    
    
    if INSTALLATION_OPTION == "helm":
        install_helm("kubeflow-istio-resources", path_dic["kubeflow_istio_resources"]["helm"])
    else:
        apply_kustomize(path_dic["kubeflow_istio_resources"]["kustomize"])
    
    build_kserve(INSTALLATION_OPTION)
    build_models_web_app(INSTALLATION_OPTION)
    build_centralDashboard(INSTALLATION_OPTION)
    build_kubeflowPipelines(INSTALLATION_OPTION)
    build_notebook(INSTALLATION_OPTION)
    build_volumesWebApp(INSTALLATION_OPTION)
    build_trainingOperator(INSTALLATION_OPTION)
    build_katib(INSTALLATION_OPTION)
    build_tensorBoard(INSTALLATION_OPTION)
    build_profile(INSTALLATION_OPTION)
    if AWS_TELEMETRY_OPTION == "enable":
        build_aws_telemetry(INSTALLATION_OPTION)

def build_aws_telemetry(INSTALLATION_OPTION):
    print("==========Installing AWS-Telemtry==========")
    if INSTALLATION_OPTION == "helm":
        install_helm("aws-telemetry", path_dic["aws_telemetry"]["helm"])
    else:
        #kustomize
        apply_kustomize(path_dic["aws_telemetry"]["kustomize"])
    retcode = kubectl_get_cronjob("aws-kubeflow-telemetry","kubeflow")
    assert retcode == 0
    print ("aws-telemetry is running!")
    

def build_certManager(INSTALLATION_OPTION):
    print("==========Installing Cert-Manager==========")
    cert_manager_chart_path = path_dic["cert_manager"]["helm"]
    if INSTALLATION_OPTION == "helm":
        cmd = f"helm install cert-manager {cert_manager_chart_path} \
        --namespace cert-manager \
        --create-namespace \
        --set installCRDs=true".split()
        build_retcode = subprocess.call(cmd)
        assert build_retcode == 0
    else:
        #kustomize
        apply_kustomize(path_dic["cert_manager"]["kustomize"])

    print("Waiting for Cert-manager to be ready ...")
    retcode = kubectl_wait_pods(pods = 'cert-manager, webhook, cainjector',namespace='cert-manager',timeout=120)
    assert retcode == 0
    print("All cert-manager pods are running!")
    

def build_istio(INSTALLATION_OPTION):
    print("==========Installing Istio==========")
    if INSTALLATION_OPTION == "helm":
        install_helm("istio-1-14", path_dic["istio"]["helm"])
    else:
        #kustomize
        apply_kustomize(path_dic["istio_crd"]["kustomize"])
        apply_kustomize(path_dic["istio_namespace"]["kustomize"])
        apply_kustomize(path_dic["istio_base"]["kustomize"])
    print("Waiting for istio to be ready ...")
    retcode = kubectl_wait_pods(pods='istio-ingressgateway, istiod', namespace='istio-system', timeout=120)
    assert retcode == 0
    print("All istio pods are running!")

def build_dex(INSTALLATION_OPTION):
    print("==========Installing Dex==========")
    if INSTALLATION_OPTION == "helm":
        install_helm("dex", path_dic["dex"]["helm"])
    else:
        apply_kustomize(path_dic["dex"]["kustomize"])
    print("Waiting for dex to be ready ...")
    retcode = kubectl_wait_pods(pods='dex', namespace='auth', timeout=120)
    assert retcode == 0
    print("All dex pods are running!")

def build_clusterLocalGateway(INSTALLATION_OPTION):
    print("==========Installing Cluster-local-gateway==========")
    if INSTALLATION_OPTION == "helm":
        install_helm("cluster-local-gateway", path_dic["cluster_local_gateway"]["helm"])
    else:
        apply_kustomize(path_dic["cluster_local_gateway"]["kustomize"])
    print("Waiting for cluster-local-gateway pods to be ready ...")
    retcode = kubectl_wait_pods(pods='cluster-local-gateway', namespace='istio-system', timeout=120)
    assert retcode == 0
    print("All cluster-local-gateway pods are running!")

def build_knativeServing(INSTALLATION_OPTION):
    print("==========Installing Knative-Serving==========")
    if INSTALLATION_OPTION == "helm":
        install_helm("knative-serving", path_dic["knative_serving"]["helm"])
    else:
        apply_kustomize(path_dic["knative_serving"]["kustomize"], crd_required="images.caching.internal.knative.dev")
    print("Waiting for knative-serving pods to be ready ...")
    retcode = kubectl_wait_pods(pods='activator, autoscaler, controller, istio-webhook, networking-istio, webhook', namespace='knative-serving', timeout=120)
    assert retcode == 0
    print("All knative-serving pods are running!")

def build_knativeEventing(INSTALLATION_OPTION):
    print("==========Installing Knative-Eventing==========")
    if INSTALLATION_OPTION=="helm":
        install_helm("knative-eventing", path_dic["knative_eventing"]["helm"])
    else:
        apply_kustomize(path_dic["knative_eventing"]["kustomize"])
    print("Waiting for knative-eventing pods to be ready ...")
    retcode = kubectl_wait_pods(pods='eventing-controller, eventing-webhook', namespace='knative-eventing', timeout=120)
    assert retcode == 0
    print("All knative-eventing pods are running!")

def build_oidcAuthService(INSTALLATION_OPTION):
    print("==========Installing OIDC-Authservice==========")
    if INSTALLATION_OPTION == "helm":
        install_helm("oidc-authservice", path_dic["oidc_authservice"]["helm"])
    else:
        apply_kustomize(path_dic["oidc_authservice"]["kustomize"])
    print("Waiting for oidc-authservice pods to be ready ...")
    retcode = kubectl_wait_pods(pods='authservice', namespace='istio-system', timeout=120)
    assert retcode == 0
    print("All oidc-authservice pods are running!")

def build_kserve(INSTALLATION_OPTION):
    print("==========Installing Kserve==========")
    if INSTALLATION_OPTION == "helm":
        install_helm("kserve", path_dic["kserve"]["helm"])
    else:
        apply_kustomize(path_dic["kserve"]["kustomize"], crd_required="clusterservingruntimes.serving.kserve.io")
    print("Waiting for kserve pods to be ready ...")
    retcode = kubectl_wait_pods(pods='kserve', namespace='kubeflow', timeout=120)
    assert retcode == 0
    print("All kserve pods are running!")

def build_models_web_app(INSTALLATION_OPTION):
    print("==========Installing Models-Web-Apps==========")
    
    if INSTALLATION_OPTION == "helm":
        install_helm("models-web-app", path_dic["models_web_app"]["helm"])
    else:
        apply_kustomize(path_dic["models_web_app"]["kustomize"])
    
    print("Waiting for models-web-app pods to be ready ...")
    retcode = kubectl_wait_pods(pods='kserve-models-web-app', namespace='kubeflow', identifier="kustomize.component")
    assert retcode == 0
    print("All kserve-models-web-app pods are running!")

def build_centralDashboard(INSTALLATION_OPTION):
    print("==========Installing Central-Dashboard==========")
    if INSTALLATION_OPTION == "helm":
        install_helm("central-dashboard", path_dic["central_dashboard"]["helm"])
    else:
        apply_kustomize(path_dic["central_dashboard"]["kustomize"])
    print("Waiting for central-dashboard pods to be ready ...")
    retcode = kubectl_wait_pods(pods='centraldashboard', namespace='kubeflow')
    assert retcode == 0
    print("All central-dashboard pods are running!")

def build_kubeflowPipelines(INSTALLATION_OPTION):
    print("==========Installing Kubeflow-Pipelines==========")
    if INSTALLATION_OPTION == "helm":
        install_helm("kubeflow-pipelines", path_dic["kubeflow_pipelines"]["helm"])
    else:
        kubectl_apply(path_dic["kubeflow_pipelines_crd"]["kustomize"])
        print("Waiting for crd/compositecontrollers.metacontroller.k8s.io to be available ...")
        retcode = kubectl_wait_crd(crd="compositecontrollers.metacontroller.k8s.io")
        assert retcode == 0
        apply_kustomize(path_dic["kubeflow_pipelines"]["kustomize"])

    print("Waiting for kubeflow-pipelines pods to be ready ...")
    retcode = kubectl_wait_pods(pods='cache-server, kubeflow-pipelines-profile-controller, \
                                      metacontroller, metadata-envoy-deployment, metadata-grpc-deployment, \
                                      metadata-writer, minio, ml-pipeline, ml-pipeline-persistenceagent, \
                                      ml-pipeline-scheduleworkflow, ml-pipeline-ui, ml-pipeline-viewer-crd, \
                                      ml-pipeline-visualizationserver, mysql, workflow-controller', 
                                 namespace='kubeflow', timeout=240)
    assert retcode == 0
    print("All kubeflow-pipelines pods are running!")

def build_notebook(INSTALLATION_OPTION):
    print("==========Installing Notebook==========")
    ##admission-webhook
    if INSTALLATION_OPTION == "helm":
        install_helm("admission-webhook", path_dic["admission_webhook"]["helm"])
    else:
        apply_kustomize(path_dic["admission_webhook"]["kustomize"])
    print("Waiting for admission-webhook pods to be ready ...")
    retcode = kubectl_wait_pods(pods='poddefaults', namespace='kubeflow')
    assert retcode == 0
    ##notebook-controller
    if INSTALLATION_OPTION == "helm":
        install_helm("notebook-controller", path_dic["notebook_controller"]["helm"])
    else:
        apply_kustomize(path_dic["notebook_controller"]["kustomize"])
    print("Waiting for notebook-controller pods to be ready ...")
    retcode = kubectl_wait_pods(pods='notebook-controller', namespace='kubeflow')
    assert retcode == 0
    ##jupyter-web-app
    if INSTALLATION_OPTION == "helm":
        install_helm("jupyter-web-app", path_dic["jupyter_web_app"]["helm"])
    else:
        apply_kustomize(path_dic["jupyter_web_app"]["kustomize"])
    print("Waiting for jupyter-web-app pods to be ready ...")
    retcode = kubectl_wait_pods(pods='jupyter-web-app', namespace='kubeflow')
    assert retcode == 0
    print("All notebook pods are running!")

def build_volumesWebApp(INSTALLATION_OPTION):
    print("==========Installing Volumes-web-app==========")
    if INSTALLATION_OPTION == "helm":
        install_helm("volumes-web-app", path_dic["volumes_web_app"]["helm"])
    else:
        apply_kustomize(path_dic["volumes_web_app"]["kustomize"])
    print("Waiting for volumes-web-app pods to be ready ...")
    retcode = kubectl_wait_pods(pods='volumes-web-app', namespace='kubeflow')
    assert retcode == 0
    print("All volumes-web-app pods are running!")

def build_tensorBoard(INSTALLATION_OPTION):
    print("==========Installing Tensor-Board==========")
    ##tensorboard-controller
    if INSTALLATION_OPTION == "helm":
        install_helm("tensorboard-controller", path_dic["tensorboard_controller"]["helm"])
    else:
        apply_kustomize(path_dic["tensorboard_controller"]["kustomize"])
    print("Waiting for tensorboard-controller pods to be ready ...")
    retcode = kubectl_wait_pods(pods='tensorboard-controller', namespace='kubeflow')
    assert retcode == 0
    ##tensorboards-web-app
    if INSTALLATION_OPTION == "helm":
        install_helm("tensorboards-web-app", path_dic["tensorboards_web_app"]["helm"])
    else:
        apply_kustomize(path_dic["tensorboards_web_app"]["kustomize"])
    print("Waiting for tensorboards-web-app pods to be ready ...")
    retcode = kubectl_wait_pods(pods='tensorboards-web-app', namespace='kubeflow')
    assert retcode == 0
    print("All tensorboard pods are running!")

def build_trainingOperator(INSTALLATION_OPTION):
    print("==========Installing Training-Operator==========")
    if INSTALLATION_OPTION == "helm":
        install_helm("training-operator", path_dic["training_operator"]["helm"])
    else:
        apply_kustomize(path_dic["training_operator"]["kustomize"])
    print("Waiting for training-operator pods to be ready ...")
    retcode = kubectl_wait_pods(pods='kubeflow-training-operator', namespace='kubeflow', identifier='control-plane')
    assert retcode == 0
    print("All training-operator pods are running!")

def build_katib(INSTALLATION_OPTION):
    print("==========Installing Katib==========")
    if INSTALLATION_OPTION == "helm":
        install_helm("katib",path_dic["katib"]["helm"])
    else:
        apply_kustomize(path_dic["katib"]["kustomize"])
    print("Waiting for katib pods to be ready ...")
    retcode = kubectl_wait_pods(pods='controller, db-manager, mysql, ui', 
                                namespace='kubeflow', timeout=240,identifier='katib.kubeflow.org/component')
    assert retcode == 0
    print("All katib pods are running!")

def build_profile(INSTALLATION_OPTION):
    print("==========Installing Profiles==========")
    ##profile-and-kfam
    
    if INSTALLATION_OPTION == "helm":
        install_helm("profiles-and-kfam", path_dic["profiles_and_kfam"]["helm"])
    else:
        apply_kustomize(path_dic["profiles_and_kfam"]["kustomize"])
    print("Waiting for profiles-and-kfam pods to be ready ...")
    retcode = kubectl_wait_pods(pods='profiles', namespace='kubeflow', identifier='kustomize.component')
    assert retcode == 0
    
    ##user_namespace
    if INSTALLATION_OPTION == "helm":
        install_helm("user-namespace", path_dic["user_namespace"]["helm"])
    else:
        apply_kustomize(path_dic["user_namespace"]["kustomize"])
    print("Waiting for user-namespace pods to be ready ...")
    ##It needs some time for the pod to show up before validating
    retcode = kubectl_get_namespace("kubeflow-user-example-com")
    assert retcode == 0
    time.sleep(15)
    retcode = kubectl_wait_pods(pods='ml-pipeline-ui-artifact, ml-pipeline-visualizationserver', namespace='kubeflow-user-example-com')
    assert retcode == 0
    print("All user-profile pods are running!")

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

    args, _ = parser.parse_known_args()
    INSTALLATION_OPTION=args.installation_option
    AWS_TELEMETRY_OPTION=args.aws_telemetry
    install_kubeflow(INSTALLATION_OPTION,AWS_TELEMETRY_OPTION)