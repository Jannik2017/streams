from nornir import InitNornir
from nornir.core.task import Task, Result
from nornir_netmiko.tasks import netmiko_send_command
from nornir_utils.plugins.tasks.files import write_file

def fetch_vyos_config(task: Task) -> Result:
    config_result = task.run(
        task=netmiko_send_command,
        command_string="show configuration commands",
        use_textfsm=True
    )
    config = config_result.result
    
    # Save config to a file (optional)
    task.run(
        task=write_file,
        content=config,
        filename=f"{task.host}-config.txt"
    )

    return Result(
        host=task.host,
        result=f"Fetched and imported config for {task.host}"
    )

def main():
    nr = InitNornir(config_file="config.yml")
    result = nr.run(task=fetch_vyos_config)
    print("type(result): ", type(result))
    print("result: ", result)
#    for host, task_results in result.items():
#        for task_result in task_results[1].result.split('\n'):
#            print(task_result)
#            print(f"{host}: {task_result}")

    for hostname, multi_result in result.items():
        print('=================', hostname, '=================')
        for task_result in multi_result:
            # Decomposing the task_result
            host = task_result.host
            name = task_result.name
            task_output = task_result.result
            failed = task_result.failed
            changed = task_result.changed
            severity_level = task_result.severity_level
            diff = task_result.diff
            exception = task_result.exception
            #traceback = task_result.traceback

            print(f"Host: {host}")
            print(f"Task Name: {name}")
            print(f"Result: {task_output}")
            print(f"Failed: {failed}")
            print(f"Changed: {changed}")
            print(f"Severity Level: {severity_level}")
            print(f"Diff: {diff}")
            print(f"Exception: {exception}")
            #print(f"Traceback: {traceback}")


if __name__ == "__main__":
    main()
