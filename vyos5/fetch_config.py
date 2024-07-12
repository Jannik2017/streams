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
    print(type(result))
    print("result: ", result)
    for host, task_results in result.items():
        print(host)
        print(task_results)
        print("1: ", task_results[1])
        for task_result in task_results[1].result.split('\n'):
            print(task_result)
            print(f"{host}: {task_result}")

if __name__ == "__main__":
    main()
