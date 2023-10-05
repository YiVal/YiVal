diff a/src/yival/cli/init.py b/src/yival/cli/init.py	(rejected hunks)
@@ -1,4 +1,4 @@
-from argparse import ArgumentTypeError, Namespace
+from argparse import Namespace
 
 from yival.wrappers.string_wrapper import StringWrapper
 
@@ -63,10 +63,12 @@ def variation_type(arg: str):
             "variations": variations,
             "generator_name": generator_name
         }
-    except ValueError:
-        raise ArgumentTypeError(
-            f"Invalid format for variation: {arg}. Expected format: key=value_type:value1,value2,...;generator_name=gen_name"
-        )
+    except ValueError as exc:
+        raise ValueError(
+            "Invalid format for variation: {}.\n"
+            "Expected format: key=value_type:value1,value2,...;\n"
+            "generator_name=gen_name".format(arg)
+        ) from exc
 
 
 def add_arguments_to(subparser):
@@ -74,7 +76,10 @@ def add_arguments_to(subparser):
     parser = subparser.add_parser(
         "init", help="Initialize an experiment configuration template."
     )
-    parser.description = "Generate a configuration template for AI experiments based on provided parameters."
+    parser.description = (
+        "Generate a configuration template for AI "
+        "experiments based on provided parameters."
+    )
     parser.set_defaults(func=init)
 
     # Basic configuration arguments
@@ -88,8 +93,10 @@ def add_arguments_to(subparser):
         type=str,
         default="dataset",
         choices=["dataset", "user", "machine_generated"],
-        help=
-        "Source type for the experiment. Options: 'dataset', 'machine_generated', or 'user'."
+        help=(
+            "Source type for the experiment. Options: "
+            "'dataset', 'machine_generated', or 'user'."
+        )
     )
 
     # Component-specific arguments
@@ -139,7 +146,10 @@ def add_arguments_to(subparser):
     parser.add_argument(
         "--custom_reader",
         type=str,
-        help="Specify custom reader in 'name:class_path:config_cls_path' format."
+        help=(
+            "Specify custom reader in "
+            "'name:class_path:config_cls_path' format."
+        )
     )
     parser.add_argument(
         "--custom_improver",
@@ -177,14 +187,18 @@ def add_arguments_to(subparser):
         "--custom_variation_generators",
         type=str,
         nargs='+',
-        help=
-        "Specify custom variation generators in 'name:class_path:config_cls_path' format."
+        help=(
+            "Specify custom variation generators in "
+            "'name:class_path:config_cls_path' format."
+        )
     )
     parser.add_argument(
         "--custom_selection_strategy",
         type=str,
-        help=
-        "Specify custom selection strategies in 'name:class_path:config_cls_path' format."
+        help=(
+            "Specify custom selection strategies in "
+            "'name:class_path:config_cls_path' format."
+        )
     )
 
 
@@ -209,8 +223,8 @@ def init(args: Namespace):
 
     custom_reader = {}
     if args.custom_reader:
-        reader_name, reader_class_path, reader_config_cls_path = args.custom_reader.split(
-            ":"
+        reader_name, reader_class_path, reader_config_cls_path = (
+            args.custom_reader.split(":")
         )
         custom_reader[reader_name] = {
             "class_path": reader_class_path,
@@ -218,8 +232,8 @@ def init(args: Namespace):
         }
     custom_improver = {}
     if args.custom_improver:
-        improver_name, improver_class_path, improver_config_cls_path = args.custom_improver.split(
-            ":"
+        improver_name, improver_class_path, improver_config_cls_path = (
+            args.custom_improver.split(":")
         )
         custom_improver[improver_name] = {
             "class_path": improver_class_path,
@@ -228,8 +242,8 @@ def init(args: Namespace):
     custom_wrappers = {}
     if args.custom_wrappers:
         for custom_wrapper in args.custom_wrappers:
-            wrapper_name, wrapper_class_path, wrapper_config_cls_path = custom_wrapper.split(
-                ":"
+            wrapper_name, wrapper_class_path, wrapper_config_cls_path = (
+                custom_wrapper.split(":")
             )
             custom_wrappers[wrapper_name] = {
                 "class_path": wrapper_class_path,
@@ -238,8 +252,8 @@ def init(args: Namespace):
     custom_evaluators = {}
     if args.custom_evaluators:
         for custom_evaluator in args.custom_evaluators:
-            evaluator_name, evaluator_class_path, evaluator_config_cls_path = custom_evaluator(
-                ":"
+            evaluator_name, evaluator_class_path, evaluator_config_cls_path = (
+                custom_evaluator.split(":")
             )
             custom_evaluators[evaluator_name] = {
                 "class_path": evaluator_class_path,
@@ -248,8 +262,8 @@ def init(args: Namespace):
     custom_data_generators = {}
     if args.custom_data_generators:
         for custom_data_generator in args.custom_data_generators:
-            data_generator_name, data_generator_class_path, data_generator_config_cls_path = custom_data_generator(
-                ":"
+            data_generator_name, data_generator_class_path, data_generator_config_cls_path = (
+                custom_data_generator.split(":")
             )
             custom_data_generators[data_generator_name] = {
                 "class_path": data_generator_class_path,
@@ -258,8 +272,8 @@ def init(args: Namespace):
     custom_variation_generators = {}
     if args.custom_variation_generators:
         for custom_variation_generator in args.custom_variation_generators:
-            variation_generator_name, variation_generator_class_path, variation_generator_config_cls_path = custom_variation_generator(
-                ":"
+            variation_generator_name, variation_generator_class_path, variation_generator_config_cls_path = (
+                custom_variation_generator.split(":")
             )
             custom_variation_generators[variation_generator_name] = {
                 "class_path": variation_generator_class_path,
@@ -268,8 +282,8 @@ def init(args: Namespace):
 
     custom_selection_strategy = {}
     if args.custom_selection_strategy:
-        strategy_name, strategy_class_path, strategy_config_cls_path = args.custom_selection_strategy.split(
-            ":"
+        strategy_name, strategy_class_path, strategy_config_cls_path = (
+            args.custom_selection_strategy.split(":")
         )
         custom_selection_strategy[strategy_name] = {
             "class_path": strategy_class_path,
