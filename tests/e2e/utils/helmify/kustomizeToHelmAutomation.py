
import os
import shutil
from e2e.utils.utils import load_yaml_file, load_multiple_yaml_files, write_yaml_file
from e2e.utils.helmify import common


def main():
    config_file_path = common.CONFIG_FILE
    cfg = load_yaml_file(file_path=config_file_path)
    kustomized_path = cfg["Kustomization Filepath"]
    helm_chart_name = cfg["Helm Chart Name"]
    helm_chart_path = cfg["Output Helm Filepath"]
    curdir = os.environ.get("PYTHONPATH", "")
    kustomizeBuild(kustomized_path, helm_chart_name)
    moveKustomizedFileToCurdir(kustomized_path, curdir, helm_chart_name)
    splitYAML(curdir, helm_chart_name)
    createHelmChart(helm_chart_path, helm_chart_name)
    moveYAMLFilesToHelmTemplate(curdir,helm_chart_path,helm_chart_name)
    findFailedConfigFiles(helm_chart_path, helm_chart_name)
    cleanup(curdir)
    generateHelmTemplate(helm_chart_path,helm_chart_name)

def kustomizeBuild(kustomized_path, helmChartName):

    KustomizedFileName = f"{helmChartName}-kustomized.yaml"
    os.chdir(f"{kustomized_path}")
    command = f"kustomize build . > {KustomizedFileName}"
    os.system(command)
    if not os.path.exists(f"{kustomized_path}/{helmChartName}-kustomized.yaml"):
        raise ValueError("kustomized yaml file is not generated.")


def moveKustomizedFileToCurdir(source, dest, helmChartName):
    KustomizedFileName = f"{helmChartName}-kustomized.yaml"
    sourceFull = f"{source}/{KustomizedFileName}"
    destFull = f"{dest}/{KustomizedFileName}"
    shutil.move(sourceFull,destFull)

def splitYAML(curdir,helmChartName):
    kindSet = set()
    KustomizedFileName = f"{helmChartName}-kustomized.yaml"
    outputPath = f"{curdir}/output"
    if os.path.isdir(outputPath) == False:
        os.mkdir(outputPath)
    
    content = load_multiple_yaml_files(file_path=f"{curdir}/{KustomizedFileName}")
    for data in content:
        kind = data['kind'] 
        if kind not in kindSet:
            kindSet.add(kind)
            if os.path.isdir(f"{curdir}/output/{kind}") == False:
                os.mkdir(f"{curdir}/output/{kind}")
        if 'namespace' in data['metadata']:
            namespace = data['metadata']['namespace']
            name = data['metadata']['name']
            outputFileName = f"{name}-{namespace}-{kind}"
        else:
            name = data['metadata']['name']
            outputFileName = f"{name}-{kind}"

        #write file into outputFile
        write_yaml_file(yaml_content=data, file_path=f"{curdir}/{outputFileName}.yaml")

        #move file to folder
        source = f"{curdir}/{outputFileName}.yaml"
        dest = f"{curdir}/output/{kind}/{outputFileName}.yaml"
        shutil.move(source,dest)
                    

def createHelmChart(helm_chart_path,helm_chart_name):
    os.chdir(f"{helm_chart_path}")
    os.system(f"helm create {helm_chart_name}")
    if not os.path.exists(f"{helm_chart_path}/{helm_chart_name}"):
        raise ValueError ("helm chart was not created successfully.")

    #cleaning up template folder
    dir = f"{helm_chart_path}/{helm_chart_name}/templates"
    shutil.rmtree(f"{dir}/tests")
    #delete all autogenerate yaml folders
    filelist = [ f for f in os.listdir(dir) if f.endswith(".yaml") ]
    for f in filelist:
        os.remove(os.path.join(dir, f))
    #delete NOTES.txt
    os.remove(f"{dir}/NOTES.txt")

    #empty values.yaml
    valueFile = f"{helm_chart_path}/{helm_chart_name}/values.yaml"
    emptyYAMLFile = None
    write_yaml_file(yaml_content=emptyYAMLFile, file_path=valueFile)
    
  


def moveYAMLFilesToHelmTemplate(curdir,helm_chart_path,helm_chart_name):
    outputPath = f"{curdir}/output"
    
    helm_dir = f"{helm_chart_path}/{helm_chart_name}"
    #move crds
    if os.path.isdir(f"{helm_dir}/crds") == False:
        os.mkdir(f"{helm_dir}/crds")
    if os.path.isdir(f"{outputPath}/CustomResourceDefinition"):
        filelist = [ f for f in os.listdir(f"{outputPath}/CustomResourceDefinition")]
        crdDestPath = f"{helm_dir}/crds"
        for f in filelist:
            shutil.move(f"{outputPath}/CustomResourceDefinition/{f}",f"{crdDestPath}/{f}")
    
    #move rest of kinds
    obj = os.scandir(outputPath)
    
    for entry in obj :
        if entry.is_dir() or entry.is_file():
            #move files to template
            if (entry.name != 'CustomResourceDefinition'):
                if os.path.isdir(f"{helm_dir}/templates/{entry.name}") == False:
                    os.mkdir(f"{helm_dir}/templates/{entry.name}")
                filelist = [ f for f in os.listdir(f"{outputPath}/{entry.name}") if f.endswith(".yaml") ]
                for f in filelist:
                    source = f"{outputPath}/{entry.name}/{f}"
                    dest = f"{helm_dir}/templates/{entry.name}/{f}"
                    shutil.move(source,dest)

def findFailedConfigFiles (helm_chart_path, helm_chart_name):
    dir = f"{helm_chart_path}/{helm_chart_name}"
    problemFileList = []
    if os.path.isdir(f"{dir}/templates/ConfigMap"):
        filelist = [ f for f in os.listdir(f"{dir}/templates/ConfigMap")]
        for f in filelist:
            content = load_multiple_yaml_files(file_path=f"{dir}/templates/ConfigMap/{f}") 
            for elem in content:
                findFailedFilesRecursiveLookup(elem,problemFileList,f)
                        
        
        if problemFileList:
            if os.path.isdir(f"{helm_chart_path}/{helm_chart_name}/failed_helm_conversions") == False:
                os.mkdir(f"{helm_chart_path}/{helm_chart_name}/failed_helm_conversions")
            print("Some Config files are conflicted with helm template formatting. Please check on files inside failed_helm_conversions folder. Replace all backticks with double quotes, then all {{ with {{`{{ and all }} with }}`}}")
            for file in problemFileList:
                source = f"{helm_chart_path}/{helm_chart_name}/templates/ConfigMap/{file}"
                dest = f"{helm_chart_path}/{helm_chart_name}/failed_helm_conversions/{file}"
                shutil.move(source,dest)

def findFailedFilesRecursiveLookup(d, problemFileList, f):
    for k, v in d.items():
        if isinstance(v, dict):
            findFailedFilesRecursiveLookup(v, problemFileList, f)
            
        else:
            flag = search(v,'`')
            if flag:
                problemFileList.append(f)
                return
                   
def search(value, searchFor):
    for v in value:
        if searchFor in v:
            return True
    return False


def cleanup(curdir):
    shutil.rmtree(f"{curdir}/output")

def generateHelmTemplate(helm_chart_path, helm_chart_name):
    os.chdir(f"{helm_chart_path}/{helm_chart_name}")
    os.system(f"helm template . > {helm_chart_name}-helmified.yaml")


if __name__ == "__main__":
    main()
