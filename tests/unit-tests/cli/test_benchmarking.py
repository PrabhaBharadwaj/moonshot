import pytest
from io import StringIO 
from unittest.mock import patch
from moonshot.integrations.cli.cli import CommandLineInterface
from moonshot.api import api_set_environment_variables
import shutil
import os

@pytest.fixture
def cli():
    return CommandLineInterface()

def run_command(cli: CommandLineInterface, command_list: list = []):
    for command in command_list:
        cli.onecmd_plus_hooks(command)

def run_command_table(cli, command):
    with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
        cli.onecmd_plus_hooks(command)
        return mock_stdout.getvalue()

def perform_assertion(cli, command_list, expected_output, capsys):
    run_command(cli, command_list)
    captured = capsys.readouterr()
    if captured.out:
        assert captured.out.rstrip() == expected_output or expected_output in captured.out.rstrip()
    else:
        assert expected_output in captured.err.rstrip()

ut_data_dir = "tests/unit-tests/src/data"
ut_sample_dir = "tests/unit-tests/common/samples"

class TestBenchmarkingCLI:
    @pytest.fixture(autouse=True)
    def init(self):
        list_of_directories = ["attack-modules", "connectors-endpoints", "context-strategies", "cookbooks", 
                               "databases", "databases-modules", "datasets", "io-modules", "metrics",
                               "prompt-templates", "recipes", "runners"]
        
        for dir_name in list_of_directories:
            os.makedirs(f"{ut_data_dir}/{dir_name}/", exist_ok=True)

        # Set environment variables for result paths
        api_set_environment_variables(
            {
                "RUNNERS": f"{ut_data_dir}/runners/",
                "DATABASES": f"{ut_data_dir}/databases/",
                "DATABASES_MODULES": f"{ut_data_dir}/databases-modules/",
                "CONNECTORS_ENDPOINTS": f"{ut_data_dir}/connectors-endpoints/",
                "IO_MODULES": f"{ut_data_dir}/io-modules/",
                "ATTACK_MODULES": f"{ut_data_dir}/attack-modules/",
                "CONTEXT_STRATEGY": f"{ut_data_dir}/context-strategies/",
                "COOKBOOKS": f"{ut_data_dir}/cookbooks/",
                "METRICS": f"{ut_data_dir}/metrics/",
                "PROMPT_TEMPLATES": f"{ut_data_dir}/prompt-templates/",
                "RECIPES": f"{ut_data_dir}/recipes/",
            }
        )

        # Copy cookbooks
        shutil.copyfile(
            f"{ut_sample_dir}/chinese-safety-cookbook.json",
            f"{ut_data_dir}/cookbooks/chinese-safety-cookbook.json",
        )

        # Copy recipes
        shutil.copyfile(
            f"{ut_sample_dir}/bbq.json",
            f"{ut_data_dir}/recipes/bbq.json",
        )
        shutil.copyfile(
            f"{ut_sample_dir}/arc.json",
            f"{ut_data_dir}/recipes/arc.json",
        )        

        # Copy dataset
        shutil.copyfile(
            f"{ut_sample_dir}/bbq-lite-age-ambiguous.json",
            f"{ut_data_dir}/datasets/bbq-lite-age-ambiguous.json",
        )

        # Copy metrics
        shutil.copyfile(
            f"{ut_sample_dir}/bertscore.py",
            f"{ut_data_dir}/metrics/bertscore.py",
        )
        shutil.copyfile(
            f"{ut_sample_dir}/bleuscore.py",
            f"{ut_data_dir}/metrics/bleuscore.py",
        )

        # Copy prompt templates
        shutil.copyfile(
            f"{ut_sample_dir}/analogical-similarity.json",
            f"{ut_data_dir}/prompt-templates/analogical-similarity.json",
        )
        shutil.copyfile(
            f"{ut_sample_dir}/mmlu.json",
            f"{ut_data_dir}/prompt-templates/mmlu.json",
        )

        # Copy attack modules
        shutil.copyfile(
            f"{ut_sample_dir}/charswap_attack_module.py",
            f"{ut_data_dir}/attack-modules/charswap_attack_module.py",
        )
        shutil.copyfile(
            f"{ut_sample_dir}/homoglyph_attack_module.py",
            f"{ut_data_dir}/attack-modules/homoglyph_attack_module.py",
        )        

        # Setup complete, proceed with tests
        yield

        # for dir_name in list_of_directories:
        #     if os.path.exists(f"{ut_data_dir}/{dir_name}"):
        #         shutil.rmtree(f"{ut_data_dir}/{dir_name}/")


    test_recipe_id = "my-unit-test-recipe"
    test_cookbook_id = "my-unit-test-cookbook"
    err_unrecognised_arg = "Error: unrecognized arguments"
    err_missing_required_arg = "Error: the following arguments are required"

    # ------------------------------------------------------------------------------
    # Creation of files
    # ------------------------------------------------------------------------------
    @pytest.mark.parametrize(
        "command_list, expected_output",
        [
            # Success: Add with missing optional args
            (
                ["add_recipe 'My unit test recipe' "
                "'hello world description?!' "
                "\"['category1','category2']\" "
                "\"['bbq-lite-age-ambiguous']\" "
                "\"['bertscore','bleuscore']\" " 
                "-p \"['analogical-similarity','mmlu']\" "
                "-t \"['tag1','tag2']\" "],
                f"[add_recipe]: Recipe ({test_recipe_id}) created."
            ),

            # Failure: Add with 1 missing required argument
            (
                ["add_recipe 'My unit test recipe' "
                "'hello world description?!' "
                "\"['category1','category2']\" "
                "\"['bbq-lite-age-ambiguous']\" "
                "-p \"['analogical-similarity','mmlu']\" "
                "-t \"['tag1','tag2']\" "
                "-a \"['charswap_attack_module']\" "
                "-g \"{'A':[80,100],'B':[60,79],'C':[40,59],'D':[20,39],'E':[0,19]}\" "],
                err_missing_required_arg
            ),

            # Failure: Add with missing required arguments
            (
                ["add_recipe 'My unit test recipe' "
                "'hello world description?!' "
                "\"['category1','category2']\" "
                "-p \"['analogical-similarity','mmlu']\" "
                "-t \"['tag1','tag2']\" "
                "-a \"['charswap_attack_module']\" "
                "-g \"{'A':[80,100],'B':[60,79],'C':[40,59],'D':[20,39],'E':[0,19]}\" "],
                err_missing_required_arg
            ),

            # Success: Help example
            (
                ["add_recipe 'My unit test recipe' "
                "'hello world description?!' "
                "\"['category1','category2']\" "
                "\"['bbq-lite-age-ambiguous']\" "
                "\"['bertscore','bleuscore']\" " 
                "-p \"['analogical-similarity','mmlu']\" "
                "-t \"['tag1','tag2']\" "
                "-a \"['charswap_attack_module']\" "
                "-g \"{'A':[80,100],'B':[60,79],'C':[40,59],'D':[20,39],'E':[0,19]}\" "],
                f"[add_recipe]: Recipe ({test_recipe_id}) created."
            ),

            # Failure: Add with non-existent dataset
            (
                ["add_recipe 'My unit test recipe' "
                "'hello world description?!' "
                "\"['category1','category2']\" "
                "\"['bbq-lite-age-ambiguous', 'bbq-lite-age-ambiguousx']\" "
                "\"['bertscore','bleuscore']\" " 
                "-p \"['analogical-similarity','mmlu']\" "
                "-t \"['tag1','tag2']\" "
                "-a \"['charswap_attack_module']\" "
                "-g \"{'A':[80,100],'B':[60,79],'C':[40,59],'D':[20,39],'E':[0,19]}\" "],
                "Dataset bbq-lite-age-ambiguousx does not exist."
            ),


            # Failure: Add with non-existent metric
            (
                ["add_recipe 'My unit test recipe' "
                "'hello world description?!' "
                "\"['category1','category2']\" "
                "\"['bbq-lite-age-ambiguous', 'bbq-lite-age-ambiguous']\" "
                "\"['bertscore','bleuscorex']\" " 
                "-p \"['analogical-similarity','mmlu']\" "
                "-t \"['tag1','tag2']\" "
                "-a \"['charswap_attack_module']\" "
                "-g \"{'A':[80,100],'B':[60,79],'C':[40,59],'D':[20,39],'E':[0,19]}\" "],
                "Metric bleuscorex does not exist."
            ),


            # Failure: Add with non-existent prompt template
            (
                ["add_recipe 'My unit test recipe' "
                "'hello world description?!' "
                "\"['category1','category2']\" "
                "\"['bbq-lite-age-ambiguous']\" "
                "\"['bertscore','bleuscore']\" " 
                "-p \"['analogical-similarity','mmlux']\" "
                "-t \"['tag1','tag2']\" "
                "-a \"['charswap_attack_module']\" "
                "-g \"{'A':[80,100],'B':[60,79],'C':[40,59],'D':[20,39],'E':[0,19]}\" "],
                "Prompt Template mmlux does not exist."
            ),

            # Failure: Add with non-existent attack module
            (
                ["add_recipe 'My unit test recipe' "
                "'hello world description?!' "
                "\"['category1','category2']\" "
                "\"['bbq-lite-age-ambiguous', 'bbq-lite-age-ambiguous']\" "
                "\"['bertscore','bleuscore']\" " 
                "-p \"['analogical-similarity','mmlu']\" "
                "-t \"['tag1','tag2']\" "
                "-a \"['charswap_attack_modulex']\" "
                "-g \"{'A':[80,100],'B':[60,79],'C':[40,59],'D':[20,39],'E':[0,19]}\" "],
                "Attack Module charswap_attack_modulex does not exist."
            ),

            # Failure: Add with incorrect parameter type for lists
            (
                ["add_recipe 'My unit test recipe' "
                "'hello world description?!' "
                "\"['category1','category2']\" "
                "\"['bbq-lite-age-ambiguous']\" "
                "\"['bertscore','bleuscore']\" " 
                "-p \"['analogical-similarity','mmlu']\" "
                "-t \"['tag1','tag2']\" "
                "-a \"'charswap_attack_module'\" "
                "-g \"{'A':[80,100],'B':[60,79],'C':[40,59],'D':[20,39],'E':[0,19]}\" "],
                "[add_recipe]: 1 validation error for api_create_recipe"              
            ),
            # Failure: Add with unknown flag           
            (
                ["add_recipe 'My unit test recipe' "
                "'hello world description?!' "
                "\"['category1','category2']\" "
                "\"['bbq-lite-age-ambiguous']\" "
                "\"['bertscore','bleuscore']\" " 
                "-p \"['analogical-similarity','mmlu']\" "
                "-t \"['tag1','tag2']\" "
                "-a \"['charswap_attack_module']\" "
                "-g \"{'A':[80,100],'B':[60,79],'C':[40,59],'D':[20,39],'E':[0,19]}\" "
                "-x o"],
                err_unrecognised_arg
            ),
        ]
    )    
    def test_add_recipe(self, cli, command_list, expected_output, capsys):
        perform_assertion(cli, command_list, expected_output, capsys)

    @pytest.mark.parametrize(
        "command_list, expected_output",
        [
            # Success: Help example
            (
                ["add_cookbook 'My unit test cookbook' 'hello world description?!' "
                "\"['analogical-similarity','arc']\""],
                "[add_cookbook]: Cookbook (my-unit-test-cookbook) created."
            ),

            # Failure: Add with 1 missing required argument
            (
                ["add_cookbook 'hello world description?!' \"['analogical-similarity','arc']\""],
                err_missing_required_arg
            ),

            # Failure: Add with missing required arguments
            (
                ["add_cookbook \"['analogical-similarity','arc']\""],
                err_missing_required_arg
            ), 

            # Failure: Add with incorrect parameter type for description
            (
                ["add_cookbook 'My unit test cookbook' 'hello world description?!' "
                "\"'this is not a list!!'\""],
                "[add_cookbook]: 1 validation error for api_create_cookbook"
            ),   

            # Failure: Add with incorrect parameter type for recipe list
            (
                ["add_cookbook 'My unit test cookbook' 'hello world description?!' "
                "\"'this is not a list!!'\""],
                "[add_cookbook]: 1 validation error for api_create_cookbook"
            ),   
            # Failure: Add with non-existent recipe
            (
                ["add_cookbook 'My unit test cookbook' 'hello world description?!' "
                "\"['analogical-similarity','auto-categorisatison']\""],
                "recipe does not exist."
            ),

            # Failure: Add with unknown flag
            (
                ["add_cookbook 'My unit test cookbook' 'hello world description?!' "
                "\"['analogical-similarity','arc']\" -n 1"],
                err_unrecognised_arg
            ),                                               
        ],
    )    
    def test_add_cookbook(self, cli, command_list, expected_output, capsys):
        perform_assertion(cli, command_list, expected_output, capsys)
 
    # ------------------------------------------------------------------------------
    # Listing and viewing data
    # ------------------------------------------------------------------------------
    @pytest.mark.parametrize(
        "command_list, expected_output",
        [
            # Success: ID
            ([f"view_recipe {test_recipe_id}"], "id: my-unit-test-recipe"),

            # Success: description
            ([f"view_recipe {test_recipe_id}"], "hello world description?!"),

            # Success: tags
            ([f"view_recipe {test_recipe_id}"], "1. tag1"),
            ([f"view_recipe {test_recipe_id}"], "2. tag2"),

            # Success: categories
            ([f"view_recipe {test_recipe_id}"], "1. category1"),
            ([f"view_recipe {test_recipe_id}"], "2. category2"),

            # Success: grading scale
            ([f"view_recipe {test_recipe_id}"], "A [80 - 100]"),
            ([f"view_recipe {test_recipe_id}"], "B [60 - 79]"),
            ([f"view_recipe {test_recipe_id}"], "C [40 - 59]"),
            ([f"view_recipe {test_recipe_id}"], "D [20 - 39]"),
            ([f"view_recipe {test_recipe_id}"], "E [0 - 19]"),

            # Success: dataset
            ([f"view_recipe {test_recipe_id}"], "bbq-lite-age-ambiguous"),

            # # Success: prompt template
            # ("analogical-similarity"),
            # ("mmlu"),

            # # Success: metric
            # ("bertscore"),
            # ("bleuscore"),

            # # Success: attack strategies
            # ("charswap_attack_module")

            # Failure: Test with unrecognised flag
            ([f"view_recipe {test_recipe_id} -x o"], err_unrecognised_arg),

            # Failure: Test with non-existment recipe
            ([f"view_recipe nope"], "[view_recipe]: No recipes found with ID")
        ]
    )
    def test_view_recipe(self, cli, command_list, expected_output, capsys):
        perform_assertion(cli, command_list, expected_output, capsys)
    
    # # def test_list_recipes(self, cli, command):
    # # pass

    # # def test_view_cookbook(self, cli):
    # # pass

    # # def test_list_cookbooks(self, cli):
    # # pass

    # # def test_view_dataset(self, cli):
    # # pass

    # # def test_list_datasets(self, cli):
    # # pass

    # # def test_view_metric(self, cli):
    # # pass

    # # def test_list_metrics(self, cli):
    # # pass

    # ------------------------------------------------------------------------------
    # Updating of files
    # ------------------------------------------------------------------------------
    @pytest.mark.parametrize(
        "command_list, expected_output",
        [
            # Success: Help example update with missing optional arguments
            ([f"update_recipe {test_recipe_id} \"[('name', 'My Updated Recipe'), ('tags', ['fairness', 'bbq'])]\""],
             "[update_recipe]: Recipe updated."
            ),

            # Success: Update every available key
            ([f"update_recipe {test_recipe_id} \"[('name', 'My Updated Recipe2'), ('tags', ['updated tag']), "
             "('description', 'updated description'), ('categories', ['updated cat 1', 'updated cat 2']), "
             " ('datasets', ['bbq-lite-age-ambiguous']), ('prompt_templates', ['analogical-similarity', 'mmlu']), "
             " ('metrics', ['bleuscore']), ('attack_modules', ['charswap_attack_module']), "
             " ('grading_scale', {'New A':[75,100],'New B':[50,74],'New C':[25,49],'New D':[0,24]}) "
             "]\""],
             "[update_recipe]: Recipe updated."
            ),

            # Failure: Update with some wrong parameter types
            ([f"update_recipe {test_recipe_id} \"[('name', ['Name should not be a list']), ('tags', ['updated tag']), "
             " ('description', 'updated description'), ('categories', ['updated cat 1', 'updated cat 2']), "
             " ('datasets', ['bbq-lite-age-ambiguous']), ('prompt_templates', ['analogical-similarity', 'mmlu']), "
             " ('metrics', ['bleuscore']), ('attack_modules', ['charswap_attack_module']), "
             " ('grading_scale', [{'New A':[75,100],'New B':[50,74],'New C':[25,49],'New D':[0,24]}]) "
             "]\""],
             "[update_recipe]: 2 validation errors for RecipeArguments"
            ),

            # Failure: Update with missing required argument
            ([f"update_recipe \"[('name', 'My Updated Recipe2'), ('tags', ['updated tag']), "
             "('description', 'updated description'), ('categories', ['updated cat 1', 'updated cat 2']), "
             " ('datasets', ['bbq-lite-age-ambiguous']), ('prompt_templates', ['analogical-similarity', 'mmlu']), "
             " ('metrics', ['bleuscore']), ('attack_modules', ['charswap_attack_module']), "
             " ('grading_scale', {'New A':[75,100],'New B':[50,74],'New C':[25,49],'New D':[0,24]}) "
             "]\""],
             err_missing_required_arg
            ),             

            # Failure: Update with non-existent dataset
            ([f"update_recipe {test_recipe_id} \"[('name', 'My Updated Recipe2'), ('tags', ['updated tag']), "
             "('description', 'updated description'), ('categories', ['updated cat 1', 'updated cat 2']), "
             " ('datasets', ['nope']), ('prompt_templates', ['analogical-similarity', 'mmlu']), "
             " ('metrics', ['bleuscore']), ('attack_modules', ['charswap_attack_module']), "
             " ('grading_scale', {'New A':[75,100],'New B':[50,74],'New C':[25,49],'New D':[0,24]}) "
             "]\""],
             "Dataset nope does not exist."
            ),             

            # Failure: Update with non-existent metric
            ([f"update_recipe {test_recipe_id} \"[('name', 'My Updated Recipe2'), ('tags', ['updated tag']), "
             "('description', 'updated description'), ('categories', ['updated cat 1', 'updated cat 2']), "
             " ('datasets', ['bbq-lite-age-ambiguous']), ('prompt_templates', ['analogical-similarity', 'mmlu']), "
             " ('metrics', ['nope']), ('attack_modules', ['charswap_attack_module']), "
             " ('grading_scale', {'New A':[75,100],'New B':[50,74],'New C':[25,49],'New D':[0,24]}) "
             "]\""],
             "Metric nope does not exist."
            ),       

            # Failure: Update with non-existent prompt template
            ([f"update_recipe {test_recipe_id} \"[('name', 'My Updated Recipe2'), ('tags', ['updated tag']), "
             "('description', 'updated description'), ('categories', ['updated cat 1', 'updated cat 2']), "
             " ('datasets', ['bbq-lite-age-ambiguous']), ('prompt_templates', ['analogical-similarity', 'nope']), "
             " ('metrics', ['bleuscore']), ('attack_modules', ['charswap_attack_module']), "
             " ('grading_scale', {'New A':[75,100],'New B':[50,74],'New C':[25,49],'New D':[0,24]}) "
             "]\""],
             "Prompt Template nope does not exist."
            ),       

            # Failure: Update with non-existent attack module
            ([f"update_recipe {test_recipe_id} \"[('name', 'My Updated Recipe2'), ('tags', ['updated tag']), "
             "('description', 'updated description'), ('categories', ['updated cat 1', 'updated cat 2']), "
             " ('datasets', ['bbq-lite-age-ambiguous']), ('prompt_templates', ['analogical-similarity', 'mmlu']), "
             " ('metrics', ['bleuscore']), ('attack_modules', ['nope']), "
             " ('grading_scale', {'New A':[75,100],'New B':[50,74],'New C':[25,49],'New D':[0,24]}) "
             "]\""],
             "Attack Module nope does not exist."
            ),       

            # Failure: Update with unknown flag
            ([f"update_recipe {test_recipe_id} \"[('name', 'My Updated Recipe2'), ('tags', ['updated tag']), "
             "('description', 'updated description'), ('categories', ['updated cat 1', 'updated cat 2']), "
             " ('datasets', ['nope']), ('prompt_templates', ['analogical-similarity', 'mmlu']), "
             " ('metrics', ['bleuscore']), ('attack_modules', ['charswap_attack_module']), "
             " ('grading_scale', {'New A':[75,100],'New B':[50,74],'New C':[25,49],'New D':[0,24]}) "
             "]\" -x o"],
             err_unrecognised_arg
            ),         

        ]
    )
    def test_update_recipe(self, cli, command_list, expected_output, capsys):
        perform_assertion(cli, command_list, expected_output, capsys)

    @pytest.mark.parametrize(
        "command_list, expected_output",
        [
            # Success: Help example
            ([f"update_cookbook {test_cookbook_id} \"[('name', 'Updated cookbook name'), "
             "('description', 'Updated description'), ('recipes', ['analogical-similarity'])]\""],
             "[update_cookbook]: Cookbook updated."
            ),

            # Success: Update some keys
            ([f"update_cookbook {test_cookbook_id} \"[('description', 'Updated cookbook description. again.')]\""],
             "[update_cookbook]: Cookbook updated."
            ),

            # Failure: Update with some wrong parameter types
            ([f"update_cookbook {test_cookbook_id} \"[('name', ['Updated cookbook name']), "
             "('description', 'Updated description'), ('recipes', ['analogical-similarity'])]\""],
             "[update_cookbook]: 1 validation error for CookbookArguments"
            ),

            # Failure: Update with missing required argument
            ([f"update_cookbook \"\""],
             err_missing_required_arg
            ),

            # # Failure: Update with unknown flag
            ([f"update_cookbook {test_cookbook_id} \"[('name', 'Updated cookbook name'), "
             "('description', 'Updated description'), ('recipes', ['analogical-similarity'])]\" -x o"],
             err_unrecognised_arg
            ),
        ]
    )
    def test_update_cookbook(self, cli, command_list, expected_output, capsys):
        perform_assertion(cli, command_list, expected_output, capsys)
    
    
    # ------------------------------------------------------------------------------
    # Running of recipes and cookbooks, and viewing the files generated
    # ------------------------------------------------------------------------------
    
    @pytest.mark.parametrize(
        "command_list, expected_output",
        [
            # Success: Help example
            ([f"run_recipe {test_recipe_id} \"['bbq','mmlu']\" \"['openai-gpt35-turbo']\" -n 1 -r 1 "
             "-s \"You are an intelligent AI\""],
             "Time taken to run"
            ),

            # Failure: Run with non-existent recipes with new runner
            ([f"run_recipe my_new_recipe \"['bbq','mmlux']\" \"['openai-gpt35-turbo']\" -n 1 -r 1 "
             "-s \"You are an intelligent AI\""],
             "No recipes found with ID"
            ),

            # Failure: Run with non-existent connector endpoint with new runner
            ([f"run_recipe my_new_recipe_two \"['bbq','mmlu']\" \"['openai-gpt35-turbox']\" -n 1 -r 1 "
             "-s \"You are an intelligent AI\""],
             "Connector endpoint openai-gpt35-turbox does not exist."
            ),

            # Failure: Run with wrong type for optional arguments (input string instead of int)
            ([f"run_recipe my_new_recipe \"['bbq','mmlu']\" \"['openai-gpt35-turbox']\" -n x -r s "
             "-s \"You are an intelligent AI\""],
             "invalid int value"
            ),

            # Failure: Run with unknown flag
            ([f"run_recipe my_new_recipe \"['bbq','mmlu']\" \"['openai-gpt35-turbox']\" -n 1 -r 1 "
             "-s \"You are an intelligent AI\" -x o"],
             err_unrecognised_arg
            ),            
        ]
    )
    def test_run_recipe(self, cli, command_list, expected_output, capsys):
        perform_assertion(cli, command_list, expected_output, capsys)


    @pytest.mark.parametrize(
        "command_list, expected_output",
        [
            # Success: Help example
            ([f"run_cookbook {test_cookbook_id} \"['chinese-safety-cookbook']\" \"['openai-gpt35-turbo']\" -n 1 -r 1 "
             "-s \"You are an intelligent AI\""],
             "Time taken to run"
            ),

            # Failure: Run with non-existent cookbook
            ([f"run_cookbook my_new_cookbook \"['chinese-safety-cookbookx']\" \"['openai-gpt35-turbo']\" -n 1 -r 1 "
             "-s \"You are an intelligent AI\""],
             "No cookbooks found with ID"
            ),

            # Failure: Run with non-existent connector endpoint with new runner
            ([f"run_cookbook my_new_cookbook_two \"['chinese-safety-cookbook']\" \"['openai-gpt35-turbox']\" -n 1 -r 1 "
             "-s \"You are an intelligent AI\""],
             "Connector endpoint openai-gpt35-turbox does not exist."
            ),


            # Failure: Run with wrong type for optional arguments (input string instead of int)
            ([f"run_cookbook my_new_cookbook \"['chinese-safety-cookbook']\" \"['openai-gpt35-turbo']\" -n x -r s "
             "-s \"You are an intelligent AI\""],
             "invalid int value"
            ),

            # Failure: Run with unknown flag
            ([f"run_cookbook my_new_cookbook\"['chinese-safety-cookbook']\" \"['openai-gpt35-turbo']\" -n 1 -r 1 "
             "-s \"You are an intelligent AI\" -x o"],
             err_unrecognised_arg
            ),            
        ]
        )
    def test_run_cookbook(self, cli, command_list, expected_output, capsys):
        perform_assertion(cli, command_list, expected_output, capsys)

    # #     def test_view_result(self, cli):
    # #         pass

    # #     def test_list_results(self, cli):
    # #         pass

    # #     def test_view_run(self, cli):
    # #         pass

    # #     def test_list_runs(self, cli):
    # #         pass

    # #     def test_view_runner(self, cli):
    # #         pass
        
    # #     def test_list_runners(self, cli):
    # #         pass


    # ------------------------------------------------------------------------------
    # Deletion of files
    # ------------------------------------------------------------------------------
    @pytest.mark.parametrize(
        "command_list, expected_output", 
        [   
            # # Success: Delete existing recipe TOFIX
            # (f"delete_recipe {test_recipe_id}", "y", "[delete_recipe]: Recipe deleted."),

            # Failure: Delete with missing argument
            ([f"delete_recipe"], err_missing_required_arg),

            # Failure: Delete with unknown flag
            ([f"delete_recipe {test_recipe_id} -x o"], err_unrecognised_arg),
        ]
    )
    def test_delete_session(self, cli, command_list, expected_output, capsys):
        perform_assertion(cli, command_list, expected_output, capsys)

    @pytest.mark.parametrize(
        "command_list, expected_output", 
        [   
            # # Success: Delete existing cookbook TOFIX
            # (f"delete_cookbook {test_cookbook_id}", "y", "[delete_cookbook]: Cookbook deleted."),

            # Failure: Delete with missing argument
            ([f"delete_cookbook"], err_missing_required_arg),

            # Failure: Delete with unknown flag
            ([f"delete_cookbook {test_cookbook_id} -x o"], err_unrecognised_arg),
        ]
    )
    def test_delete_cookbook(self, cli, command_list, expected_output, capsys):
        perform_assertion(cli, command_list, expected_output, capsys)

    # # def test_delete_dataset(self, cli):
    # #     pass

    # # def test_delete_metrics(self, cli):
    # #     pass    

    # # def test_delete_result(self, cli):
    # # pass

    # # def test_delete_runner(self, cli):
    # # pass
