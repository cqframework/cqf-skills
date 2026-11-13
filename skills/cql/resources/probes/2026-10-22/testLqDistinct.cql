library testLqDistinct

define "NoReturn": ({ 1, 1, 2 }) X
define "WhereOnly": ({ 1, 1, 2 }) X where X > 0
define "ReturnDefault": ({ 1, 1, 2 }) X return X
define "ReturnAll": ({ 1, 1, 2 }) X return all X
define "ReturnDistinct": ({ 1, 1, 2 }) X return distinct X
define "DistinctOp": distinct { 1, 1, null, null }
define "UnionDedup": { 1, 1, 2 } union { 2, 3 }
define "IntersectDedup": { 1, 1, 2 } intersect { 1, 1 }
define "ExceptDedup": { 1, 1, 2 } except { 2 }
define "FlattenKeeps": flatten { { 1, 1 }, { 1 } }
