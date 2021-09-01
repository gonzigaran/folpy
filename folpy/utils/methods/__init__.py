#!/usr/bin/env python
# -*- coding: utf8 -*-

from .substructures import (
                substructures_downup,
                substructures_updown,
                substructures_by_maximals)
from .subuniverses import (
                            subuniverses,
                            subuniverse,
                            is_subuniverse,
                            is_subuniverse_for_lattices
                          )

substructures = substructures_by_maximals
