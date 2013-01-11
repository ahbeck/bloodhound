#  Licensed to the Apache Software Foundation (ASF) under one
#  or more contributor license agreements.  See the NOTICE file
#  distributed with this work for additional information
#  regarding copyright ownership.  The ASF licenses this file
#  to you under the Apache License, Version 2.0 (the
#  "License"); you may not use this file except in compliance
#  with the License.  You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing,
#  software distributed under the License is distributed on an
#  "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
#  KIND, either express or implied.  See the License for the
#  specific language governing permissions and limitations
#  under the License.

import re

from trac.hooks import EnvironmentFactoryBase, GlobalHooksBase
import trac.env
import trac.db.util

from multiproduct.dbcursor import BloodhoundIterableCursor
from multiproduct.env import Environment, ProductEnvironment

PRODUCT_RE = re.compile(r'^/products/(?P<pid>[^/]*)(?P<pathinfo>.*)')

class MultiProductEnvironmentFactory(EnvironmentFactoryBase):
    def open_environment(self, environ, env_path, global_env, use_cache=False):
        env = pid = None
        path_info = environ.get('PATH_INFO')
        if not path_info:
            return env
        m = PRODUCT_RE.match(path_info)
        if m:
            pid = m.group('pid')
        if pid:
            env = ProductEnvironment(global_env, pid)
        return env

class MultiProductGlobalHooks(GlobalHooksBase):
    def install_hooks(self, environ, env_path):
        trac.env.Environment = Environment
        trac.db.util.IterableCursor = BloodhoundIterableCursor