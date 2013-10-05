# Copyright (c) 2012 OpenStack, LLC.
# All Rights Reserved.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

from oslo.config import cfg

from nova.openstack.common import log as logging
from nova.scheduler import filters

LOG = logging.getLogger(__name__)

project_host_default_filter = cfg.ListOpt("project_host_default_filter", default=[],
                         help="default host filter.")

project_host_map = cfg.MultiStrOpt("project_host_map", default=[],
                         help="this map indicates that the relation between hosts and the projects.")

CONF = cfg.CONF
CONF.register_opt(project_host_map)
CONF.register_opt(project_host_default_filter)

"""
#nova.conf
project_host_map=<project_id>,<allow_host_name1>,<allow_host_name2>,...
#set default don't use host
project_host_default_filter=<deny_host_name1>,<deny_host_name2>
"""
#
# Use this map indicates that the relation between hosts and the projects.
# by cyfang 2013/10/04

class ProjectHostFilter(filters.BaseHostFilter):
    """Filters Hosts by Project-Host Mapping."""
    def __init__(self):
        self.map={}
        for map_str in CONF.project_host_map:
            items = map_str.split(",")
            assign_project_id=items.pop(0)
            self.map[assign_project_id]=items

    def host_passes(self, host_state, filter_properties):
        spec = filter_properties.get('request_spec', {})
        props = spec.get('instance_properties', {})
        project_id = props.get('project_id')
    host_name = host_state.service['host']
        if project_id in self.map:
            return host_name in self.map[project_id]
        return not host_name in CONF.project_host_default_filter

#debug use
if __name__=="__main__":
    import os,sys
    from nova import config
    try:
        config.parse_args(sys.argv)
        logging.setup("nova")
    except cfg.ConfigFilesNotFoundError:
        cfgfile = CONF.config_file[-1] if CONF.config_file else None
        if cfgfile and not os.access(cfgfile, os.R_OK):
            st = os.stat(cfgfile)
            print _("Could not read %s. Re-running with sudo") % cfgfile
            try:
                os.execvp('sudo', ['sudo', '-u', '#%s' % st.st_uid] + sys.argv)
            except Exception:
                print _('sudo failed, continuing as if nothing happened')

        print _('Please re-run nova-manage as root.')
        sys.exit(2)
    print CONF.project_host_default_filter
    print CONF.project_host_map
    filter = ProjectHostFilter()
    print filter.map

