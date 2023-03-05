from ....utils.ioUtils import write_Int32, write_uInt32, write_Int16, write_xyz, write_float, write_char, write_string, write_uInt16, SmartIO, write_byte, write_float16
from ....utils.util import *
from time import time

def create_wmb_batches(wmb_file, data, wmb4=False):
    wmb_file.seek(data.batches_Offset)

    for batch in data.batches.batches:
        write_uInt32(wmb_file, batch.vertexGroupIndex)                  # vertexGroupIndex
        if not wmb4:
            write_Int32(wmb_file, batch.boneSetIndex)                   # boneSetIndex
        write_uInt32(wmb_file, batch.vertexStart)                       # vertexStart
        write_uInt32(wmb_file, batch.indexStart)                        # indexStart
        write_uInt32(wmb_file, batch.numVertexes)                       # numVertexes
        write_uInt32(wmb_file, batch.numIndexes)                        # numIndexes
        if not wmb4:
            write_uInt32(wmb_file, batch.numPrimitives)                 # numPrimitives

def create_wmb_batch_supplement(wmb_file, data): # wmb4
    wmb_file.seek(data.batchDescPointer)
    
    for index, offset in enumerate(data.batchDescriptions.batchOffsets):
        if offset == -1:
            write_uInt32(wmb_file, 0)
        else:
            write_uInt32(wmb_file, offset)   # batch data group pointer
        
        write_uInt32(wmb_file, len(data.batchDescriptions.batchData[index])) # batch data group count
    
    for index, group in enumerate(data.batchDescriptions.batchData):
        if len(group) == 0:
            continue
        wmb_file.seek(data.batchDescriptions.batchOffsets[index])
        for batch in group:
            #print(batch)
            write_uInt32(wmb_file, batch[0]) # batchIndex
            write_uInt32(wmb_file, batch[1]) # meshIndex
            write_uInt16(wmb_file, batch[2]) # materialIndex
            write_uInt16(wmb_file, batch[3]) # boneSetsIndex
            write_uInt32(wmb_file, 0)        # unknown10, hopefully just padding
            # TODO fuck it wasn't padding, sometimes 0x100 sometimes not

def create_wmb_boneIndexTranslateTable(wmb_file, data):
    wmb_file.seek(data.boneIndexTranslateTable_Offset)

    for entry in data.boneIndexTranslateTable.firstLevel:    # firstLevel
        write_Int16(wmb_file, entry)

    for entry in data.boneIndexTranslateTable.secondLevel:   # secondLevel
        write_Int16(wmb_file, entry)

    for entry in data.boneIndexTranslateTable.thirdLevel:    # thirdLevel
        write_Int16(wmb_file, entry)

def create_wmb_boneMap(wmb_file, data):
    wmb_file.seek(data.boneMap_Offset)

    for boneMap in data.boneMap.boneMap:
        write_Int32(wmb_file, boneMap)

def create_wmb_boneSet(wmb_file, data, wmb4=False):
    wmb_file.seek(data.boneSets_Offset)

    for boneSet in data.boneSet.boneSet:
        write_uInt32(wmb_file, boneSet[0])
        write_uInt32(wmb_file, boneSet[1])
    
    if wmb4:
        wmb_file.seek(data.boneSet.boneSet[0][0])
    
    for boneSet in data.boneSet.boneSet:
        for entry in boneSet[2]:
            if wmb4:
                write_byte(wmb_file, entry)
            else:
                write_Int16(wmb_file, entry)

def create_wmb_bones(wmb_file, data, wmb4=False):
    wmb_file.seek(data.bones_Offset)

    for bone in data.bones.bones:               # [ID, parentIndex, localPosition.xyz, localRotation.xyz, localScale.xyz, position.xyz, rotation.xyz, scale.xyz, tPosition.xyz]
        write_Int16(wmb_file, bone[0])          # ID
        if wmb4:
            write_Int16(wmb_file, 0)       # unknown02
        write_Int16(wmb_file, bone[1])   # parentIndex
        if wmb4:
            write_Int16(wmb_file, 0)       # rotationOrder or something
        write_xyz(wmb_file, bone[2])    # localPosition.xyx
        if not wmb4:
            write_xyz(wmb_file, bone[3])   # localRotation.xyz
            write_xyz(wmb_file, bone[4])   # localScale.xyz
        write_xyz(wmb_file, bone[5])    # position.xyz
        if not wmb4:
            write_xyz(wmb_file, bone[6])   # rotation.xyz
            write_xyz(wmb_file, bone[7])   # scale.xyz
            write_xyz(wmb_file, bone[8])   # tPosition.xyz

def create_wmb_colTreeNodes(wmb_file, data):
    wmb_file.seek(data.colTreeNodes_Offset)

    for colTreeNode in data.colTreeNodes.colTreeNodes:                # [p1, p2, left, right]
        for entry in colTreeNode[0]:                                  # p1
            write_float(wmb_file, entry)
        for entry in colTreeNode[1]:                                  # p2
            write_float(wmb_file, entry)
        write_Int32(wmb_file, colTreeNode[2])                              # left
        write_Int32(wmb_file, colTreeNode[3])                              # right

def create_wmb_header(wmb_file, data, wmb4=False):

    print('Writing header:')
    for char in ('WMB3' if not wmb4 else 'WMB4'):               # id
        write_char(wmb_file, char)                                 
    write_uInt32(wmb_file, (0x20160116 if not wmb4 else 0))     # version
    if not wmb4:
        write_Int32(wmb_file, 0)                                    # unknownA
        if data.vertexGroups.vertexGroups[0].vertexFlags in [4, 5] and data.numBones > 0:
            write_Int16(wmb_file, 8)                                    # flags
            write_Int16(wmb_file, 0)                                    # referenceBone
        elif data.vertexGroups.vertexGroups[0].vertexFlags in [5, 14]:
            write_Int16(wmb_file, 8)                                    
            write_Int16(wmb_file, -1) 
        else:
            write_Int16(wmb_file, 10)                                    
            write_Int16(wmb_file, -1)
        
        boundingBoxXYZ, boundingBoxUVW = getGlobalBoundingBox()
        write_xyz(wmb_file, boundingBoxXYZ)                        # boundingBox: x y z 
        write_xyz(wmb_file, boundingBoxUVW)                        #              u v w

        offsetBones = data.bones_Offset
        write_uInt32(wmb_file, offsetBones)                          # offsetBones
        print(' + offsetBones: ', hex(offsetBones))

        numBones = data.numBones
        write_uInt32(wmb_file, numBones)                            # numBones
        print(' + numBones: ', numBones)

        offsetBoneIndexTranslateTable = data.boneIndexTranslateTable_Offset
        write_uInt32(wmb_file, offsetBoneIndexTranslateTable)       # offsetBoneIndexTranslateTable
        print(' + offsetBoneIndexTranslateTable: ', hex(offsetBoneIndexTranslateTable))

        if hasattr(data, 'boneIndexTranslateTable'):
            boneTranslateTableSize = data.boneIndexTranslateTable.boneIndexTranslateTable_StructSize
        else:
            boneTranslateTableSize = 0
        write_uInt32(wmb_file, boneTranslateTableSize)              # boneTranslateTableSize
        print(' + boneTranslateTableSize: ', boneTranslateTableSize)

        offsetVertexGroups = data.vertexGroups_Offset
        write_uInt32(wmb_file, offsetVertexGroups)                  # offsetVertexGroups
        print(' + offsetVertexGroups: ', hex(offsetVertexGroups))

        numVertexGroups = len(data.vertexGroups.vertexGroups)
        write_uInt32(wmb_file, numVertexGroups)                     # numVertexGroups
        print(' + numVertexGroups: ', numVertexGroups)

        offsetBatches = data.batches_Offset
        write_uInt32(wmb_file, offsetBatches)                       # offsetBatches
        print(' + offsetBatches: ', hex(offsetBatches))

        numBatches = len(data.batches.batches)
        write_uInt32(wmb_file, numBatches)                          # numBatches
        print(' + numBatches: ', numBatches)

        offsetLods = data.lods_Offset
        write_uInt32(wmb_file, offsetLods)                          # offsetLods
        print(' + offsetLods: ', hex(offsetLods))

        numLods = data.lodsCount                                    
        write_uInt32(wmb_file, numLods)                             # numLods
        print(' + numLods: ', numLods)

        offsetColTreeNodes = data.colTreeNodes_Offset                                      
        write_uInt32(wmb_file, offsetColTreeNodes)                  # offsetColTreeNodes
        print(' + offsetColTreeNodes: ', hex(offsetColTreeNodes))

        numColTreeNodes = data.colTreeNodesCount    
        write_uInt32(wmb_file, numColTreeNodes)                     # numColTreeNodes
        print(' + numColTreeNodes: ', numColTreeNodes)

        offsetBoneMap = data.boneMap_Offset
        write_uInt32(wmb_file, offsetBoneMap)                       # offsetBoneMap
        print(' + offsetBoneMap: ', hex(offsetBoneMap))

        numBoneMap = data.numBoneMap
        write_uInt32(wmb_file, numBoneMap)                          # numBoneMap/boneMapSize
        print(' + numBoneMap: ', numBoneMap)

        offsetBoneSets = data.boneSets_Offset                
        write_uInt32(wmb_file, offsetBoneSets)                      # offsetBoneSets
        print(' + offsetBoneSets: ', hex(offsetBoneSets))

        if hasattr(data, 'boneSet'):
            numBoneSets = len(data.boneSet.boneSet)   
        else:
            numBoneSets = 0                          
        write_uInt32(wmb_file, numBoneSets)                         # numBoneSets
        print(' + numBoneSets: ', numBoneSets)

        offsetMaterials = data.materials_Offset
        write_uInt32(wmb_file, offsetMaterials)                     # offsetMaterials
        print(' + offsetMaterials: ', hex(offsetMaterials))

        numMaterials = len(data.materials.materials)
        write_uInt32(wmb_file, numMaterials)                        # numMaterials
        print(' + numMaterials: ', numMaterials)

        offsetMeshes = data.meshes_Offset
        write_uInt32(wmb_file, offsetMeshes)                        # offsetMeshes
        print(' + offsetMeshes: ', hex(offsetMeshes))

        numMeshes = len(data.meshes.meshes)
        write_uInt32(wmb_file, numMeshes)                           # numMeshes
        print(' + numMeshes: ', numMeshes)

        offsetMeshMaterials = data.meshMaterials_Offset
        write_uInt32(wmb_file, offsetMeshMaterials)                  # offsetMeshMaterials
        print(' + offsetMeshMaterial: ', hex(offsetMeshMaterials))

        numMeshMaterials = len(data.meshMaterials.meshMaterials)
        write_uInt32(wmb_file, numMeshMaterials)                    # numMeshMaterials
        print(' + numMeshMaterials: ', numMeshMaterials)

        offsetUnknown0 = data.unknownWorldData_Offset
        write_uInt32(wmb_file, offsetUnknown0)                      # offsetUnknown0
        print(' + offsetUnknown0: ', hex(offsetUnknown0))

        numUnknown0 = data.unknownWorldDataCount
        write_uInt32(wmb_file, numUnknown0)                          # numUnknown0
        print(' + numUnknown0: ', numUnknown0)
    else:
        write_uInt32(wmb_file, 0x137 if data.vertexGroups.vertexGroups[0].vertexFlags == 0 else 0x10337) # TODO make this read the vertex format
        
        write_Int16(wmb_file, 0 if data.numBones > 0 else -1) # TODO should be unsigned?
        write_Int16(wmb_file, -1) # TODO flags
        
        boundingBoxXYZ, boundingBoxUVW = getGlobalBoundingBox()
        write_xyz(wmb_file, boundingBoxXYZ)                        # boundingBox: x y z 
        write_xyz(wmb_file, boundingBoxUVW)                        #              u v w
        
        offsetVertexGroups = data.vertexGroups_Offset
        write_uInt32(wmb_file, offsetVertexGroups)                  # offsetVertexGroups
        print(' + offsetVertexGroups:           ', hex(offsetVertexGroups))

        numVertexGroups = len(data.vertexGroups.vertexGroups)
        write_uInt32(wmb_file, numVertexGroups)                     # numVertexGroups
        print(' + numVertexGroups:              ', numVertexGroups)
        
        offsetBatches = data.batches_Offset
        write_uInt32(wmb_file, offsetBatches)                       # offsetBatches
        print(' + offsetBatches:                ', hex(offsetBatches))

        numBatches = len(data.batches.batches)
        write_uInt32(wmb_file, numBatches)                          # numBatches
        print(' + numBatches:                   ', numBatches)
        
        batchDescPointer = data.batchDescPointer
        write_uInt32(wmb_file, batchDescPointer)
        print(' + batchDescPointer:             ', hex(batchDescPointer))
        
        offsetBones = data.bones_Offset
        write_uInt32(wmb_file, offsetBones)                          # offsetBones
        print(' + offsetBones:                  ', hex(offsetBones))

        numBones = data.numBones
        write_uInt32(wmb_file, numBones)                            # numBones
        print(' + numBones:                     ', numBones)
        
        offsetBoneIndexTranslateTable = data.boneIndexTranslateTable_Offset
        write_uInt32(wmb_file, offsetBoneIndexTranslateTable)       # offsetBoneIndexTranslateTable
        print(' + offsetBoneIndexTranslateTable:', hex(offsetBoneIndexTranslateTable))

        if hasattr(data, 'boneIndexTranslateTable'):
            boneTranslateTableSize = data.boneIndexTranslateTable.boneIndexTranslateTable_StructSize
        else:
            boneTranslateTableSize = 0
        write_uInt32(wmb_file, boneTranslateTableSize)              # boneTranslateTableSize
        print(' + boneTranslateTableSize:       ', boneTranslateTableSize)
        
        offsetBoneSets = data.boneSets_Offset                
        write_uInt32(wmb_file, offsetBoneSets)                      # offsetBoneSets
        print(' + offsetBoneSets:               ', hex(offsetBoneSets))

        if hasattr(data, 'boneSet'):
            numBoneSets = len(data.boneSet.boneSet)   
        else:
            numBoneSets = 0                          
        write_uInt32(wmb_file, numBoneSets)                         # numBoneSets
        print(' + numBoneSets:                  ', numBoneSets)
        
        offsetMaterials = data.materials_Offset
        write_uInt32(wmb_file, offsetMaterials)                     # offsetMaterials
        print(' + offsetMaterials:              ', hex(offsetMaterials))

        numMaterials = len(data.materials.materials)
        write_uInt32(wmb_file, numMaterials)                        # numMaterials
        print(' + numMaterials:                 ', numMaterials)
        
        # TODO texture class
        offsetTextures = 0#data.textures_Offset
        write_uInt32(wmb_file, offsetTextures)                     # offsetMaterials
        print(' + offsetTextures:               ', hex(offsetTextures))

        numTextures = 0#len(data.textures.textures)
        write_uInt32(wmb_file, numTextures)                        # numMaterials
        print(' + numTextures:                  ', numTextures)
        
        offsetMeshes = data.meshes_Offset
        write_uInt32(wmb_file, offsetMeshes)                        # offsetMeshes
        print(' + offsetMeshes:                 ', hex(offsetMeshes))

        numMeshes = len(data.meshes.meshes)
        write_uInt32(wmb_file, numMeshes)                           # numMeshes
        print(' + numMeshes:                    ', numMeshes)
        
        write_uInt32(wmb_file, 0xda422) # unknown, pointer?

def create_wmb_lods(wmb_file, data):
    wmb_file.seek(data.lods_Offset)

    lods = data.lods.lods
    for lod in lods:
        write_uInt32(wmb_file, lod.offsetName)                 # offsetName
        write_Int32(wmb_file, lod.lodLevel)                    # lodLevel
        write_uInt32(wmb_file, lod.batchStart)                 # batchStart
        write_uInt32(wmb_file, lod.offsetBatchInfos)           # offsetBatchInfos
        write_uInt32(wmb_file, lod.numBatchInfos)              # numBatchInfos

    for lod in lods:
        for batchInfo in lod.batchInfos:                       # [vertexGroupIndex, meshIndex, materialIndex, colTreeNodeIndex, meshMatPairIndex, indexToUnknown1]
            write_uInt32(wmb_file, batchInfo[0])                # vertexGroupIndex
            write_uInt32(wmb_file, batchInfo[1])                # meshIndex
            write_uInt32(wmb_file, batchInfo[2])                # materialIndex
            write_Int32(wmb_file, batchInfo[3])                 # colTreeNodeIndex
            write_uInt32(wmb_file, batchInfo[4])                # meshMatPairIndex
            write_Int32(wmb_file, batchInfo[5])                 # indexToUnknown1
        
        write_string(wmb_file, lod.name)                       # name

def create_wmb_materials(wmb_file, data, wmb4=False):
    wmb_file.seek(data.materials_Offset)

    for material in data.materials.materials:
        for val in material.unknown0:                           # unknown0
            write_uInt16(wmb_file, val)
        if not wmb4:
            write_uInt32(wmb_file, material.offsetName)           # offsetName
        write_uInt32(wmb_file, material.offsetShaderName)       # offsetShaderName
        if wmb4:
            write_uInt32(wmb_file, material.offsetTextures)
            write_uInt32(wmb_file, 0) # unknown08. pointer?
            write_uInt32(wmb_file, material.offsetParameterGroups)
            write_uInt16(wmb_file, material.numTextures)
            write_uInt16(wmb_file, 0) # should be 5
            write_uInt16(wmb_file, 0) # mystery value
            write_uInt16(wmb_file, material.numParameterGroups)
        if not wmb4:
            write_uInt32(wmb_file, material.offsetTechniqueName)  # offsetTechniqueName
            write_uInt32(wmb_file, material.unknown1)             # unknown1
            write_uInt32(wmb_file, material.offsetTextures)       # offsetTextures
            write_uInt32(wmb_file, material.numTextures)          # numTextures
            write_uInt32(wmb_file, material.offsetParameterGroups)  # offsetParameterGroups
            write_uInt32(wmb_file, material.numParameterGroups)     # numParameterGroups
            write_uInt32(wmb_file, material.offsetVariables)        # offsetVariables
            write_uInt32(wmb_file, material.numVariables)           # numVariables
    for material in data.materials.materials:
        write_string(wmb_file, material.name)                   # name
        write_string(wmb_file, material.shaderName)             # shaderName
        write_string(wmb_file, material.techniqueName)          # techniqueName
        for texture in material.textures:                       # [offsetName, texture, name]
            write_uInt32(wmb_file, texture[0])
            write_uInt32(wmb_file, int(texture[1], 16))
        for texture in material.textures:
            write_string(wmb_file, texture[2])
        for parameterGroup in material.parameterGroups:         # [index, offsetParameters, numParameters, parameters]
            write_Int32(wmb_file, parameterGroup[0])
            write_uInt32(wmb_file, parameterGroup[1])
            write_uInt32(wmb_file, parameterGroup[2])
        for parameterGroup in material.parameterGroups:
            for value in parameterGroup[3]:
                write_float(wmb_file, value)
        for variable in material.variables:                     # [offsetName, value, name]
            write_uInt32(wmb_file, variable[0])
            write_float(wmb_file, variable[1])
        for variable in material.variables:
            write_string(wmb_file, variable[2])

def create_wmb_meshMaterials(wmb_file, data):
    wmb_file.seek(data.meshMaterials_Offset)

    for meshMaterial in data.meshMaterials.meshMaterials:                # [meshID, materialID]
        write_uInt32(wmb_file, meshMaterial[0])                          # meshID
        write_uInt32(wmb_file, meshMaterial[1])                          # materialID

def create_wmb_meshes(wmb_file, data):
    wmb_file.seek(data.meshes_Offset)

    for mesh in data.meshes.meshes:
        write_uInt32(wmb_file, mesh.nameOffset)             # nameOffset
        for val in mesh.boundingBox:                        # boundingBox [x, y, z, u, v, m]
            write_float(wmb_file, val)
        write_uInt32(wmb_file, mesh.offsetMaterials)        # offsetMaterials
        write_uInt32(wmb_file, mesh.numMaterials)           # numMaterials
        write_uInt32(wmb_file, mesh.offsetBones)            # offsetBones
        write_uInt32(wmb_file, mesh.numBones)               # numBones

    for mesh in data.meshes.meshes:
        write_string(wmb_file, mesh.name)                   # name
        for material in mesh.materials:
            write_uInt16(wmb_file, material)                # materials
        if mesh.numBones != 0:
            for bone in mesh.bones:
                write_uInt16(wmb_file, bone)                    # bones

def create_wmb_unknownWorldData(wmb_file, data):
    wmb_file.seek(data.unknownWorldData_Offset)

    for unknownWorldData in data.unknownWorldData.unknownWorldData:                # 6 values
        for entry in unknownWorldData:                                  
            wmb_file.write(entry)

def create_wmb_vertexGroups(wmb_file, data, wmb4=False):
    wmb_file.seek(data.vertexGroups_Offset)
    
    for vertexGroup in data.vertexGroups.vertexGroups:
        write_uInt32(wmb_file, vertexGroup.vertexOffset)            # vertexOffset
        write_uInt32(wmb_file, vertexGroup.vertexExDataOffset)      # vertexExDataOffset
        for val in vertexGroup.unknownOffset:                       # unknownOffset
            write_uInt32(wmb_file, val)
        if not wmb4:
            write_uInt32(wmb_file, vertexGroup.vertexSize)              # vertexSize
            write_uInt32(wmb_file, vertexGroup.vertexExDataSize)        # vertexExDataSize
            for val in vertexGroup.unknownSize:                         # unknownSize
                write_uInt32(wmb_file, val)
        print("NumVertexes:", hex(vertexGroup.numVertexes))
        write_Int32(wmb_file, vertexGroup.numVertexes)              # numVertexes
        if not wmb4:
            write_Int32(wmb_file, vertexGroup.vertexFlags)              # vertexFlags
        write_Int32(wmb_file, vertexGroup.indexBufferOffset)        # indexBufferOffset
        write_Int32(wmb_file, vertexGroup.numIndexes)               # numIndexes
    
    fourbytes = SmartIO.makeFormat(SmartIO.uint8, SmartIO.uint8, SmartIO.uint8, SmartIO.uint8)
    writePos = SmartIO.makeFormat(SmartIO.float, SmartIO.float, SmartIO.float)
    writeTangent = fourbytes
    writeNormal = SmartIO.makeFormat(SmartIO.float16, SmartIO.float16, SmartIO.float16, SmartIO.float16)
    if wmb4:
        writeNormal = SmartIO.makeFormat(SmartIO.int8, SmartIO.int8, SmartIO.int8, SmartIO.int8)
    writeBoneIndexes = fourbytes
    writeBoneWeights = fourbytes
    writeUV = SmartIO.makeFormat(SmartIO.float16, SmartIO.float16)
    writeColor = fourbytes
    
    for vertexGroup in data.vertexGroups.vertexGroups:
        wmb_file.seek(vertexGroup.vertexOffset)
        for vertex in vertexGroup.vertexes:                         # [position.xyz, tangents, normal, uv_maps, boneIndexes, boneWeights, color]
            writePos.write(wmb_file, vertex[0])
            if not wmb4:
                writeTangent.write(wmb_file, vertex[1])
            writeUV.write(wmb_file, vertex[3][0]) # UVMap 1
            
            if vertexGroup.vertexFlags == 0:                        # Normal
                writeNormal.write(wmb_file, vertex[2])
            if wmb4:
                writeTangent.write(wmb_file, vertex[1])
            if vertexGroup.vertexFlags in {1, 4, 5, 12, 14}:
                writeUV.write(wmb_file, vertex[3][1]) # UVMap 2
            if vertexGroup.vertexFlags in {7, 10, 11} or wmb4:
                writeBoneIndexes.write(wmb_file, vertex[4])
                writeBoneWeights.write(wmb_file, vertex[5])
            if vertexGroup.vertexFlags in {4, 5, 12, 14}:
                writeColor.write(wmb_file, vertex[6])
            
        if vertexGroup.vertexExDataOffset > 0:
            wmb_file.seek(vertexGroup.vertexExDataOffset)
        for vertexExData in vertexGroup.vertexesExData:             # [normal, uv_maps, color]
            if vertexGroup.vertexFlags in {1, 4}:                   # [1, 4]
                # for val in vertexExData[0]:                         # normal
                #     write_float16(wmb_file, val)
                writeNormal.write(wmb_file, vertexExData[0])
            elif vertexGroup.vertexFlags == 5:                      # [5]
                # for val in vertexExData[0]:                         # normal
                #     write_float16(wmb_file, val)
                writeNormal.write(wmb_file, vertexExData[0])
                # for val in vertexExData[1][0]:                      # UVMap 3
                #     write_float16(wmb_file, val)
                writeUV.write(wmb_file, vertexExData[1][0])
            elif vertexGroup.vertexFlags == 7:                      # [7]
                # for val in vertexExData[1][0]:                      # UVMap 1
                #     write_float16(wmb_file, val)
                writeUV.write(wmb_file, vertexExData[1][0])
                # for val in vertexExData[0]:                         # normal
                #     write_float16(wmb_file, val)
                writeNormal.write(wmb_file, vertexExData[0])
            elif vertexGroup.vertexFlags == 10:                     # [10]
                # for val in vertexExData[1][0]:                      # UVMap 1
                #     write_float16(wmb_file, val)
                writeUV.write(wmb_file, vertexExData[1][0])
                # for val in vertexExData[2]:                         # Color                               
                #     write_byte(wmb_file, val)
                writeColor.write(wmb_file, vertexExData[2])
                # for val in vertexExData[0]:                         # normal
                #     write_float16(wmb_file, val)
                writeNormal.write(wmb_file, vertexExData[0])
            elif vertexGroup.vertexFlags == 11:                     # [11]
                # for val in vertexExData[1][0]:                      # UVMap 1
                #     write_float16(wmb_file, val)
                writeUV.write(wmb_file, vertexExData[1][0])
                # for val in vertexExData[2]:                         # Color
                #     write_byte(wmb_file, val)
                writeColor.write(wmb_file, vertexExData[2])
                # for val in vertexExData[0]:                         # normal
                #     write_float16(wmb_file, val)
                writeNormal.write(wmb_file, vertexExData[0])
                # for val in vertexExData[1][1]:                      # UVMap 2
                #     write_float16(wmb_file, val)
                writeUV.write(wmb_file, vertexExData[1][1])
            elif vertexGroup.vertexFlags == 12:                     # [12]
                # for val in vertexExData[0]:                         # normal
                #     write_float16(wmb_file, val)
                writeNormal.write(wmb_file, vertexExData[0])
                # for val in vertexExData[1][0]:                      # UVMap 3
                #     write_float16(wmb_file, val)
                writeUV.write(wmb_file, vertexExData[1][0])
                # for val in vertexExData[1][1]:                      # UVMap 4
                #     write_float16(wmb_file, val)
                writeUV.write(wmb_file, vertexExData[1][1])
                # for val in vertexExData[1][2]:                      # UVMap 5
                #     write_float16(wmb_file, val)
                writeUV.write(wmb_file, vertexExData[1][2])
            elif vertexGroup.vertexFlags == 14:                     # [14]
                # for val in vertexExData[0]:                         # normal
                #     write_float16(wmb_file, val)
                writeNormal.write(wmb_file, vertexExData[0])
                # for val in vertexExData[1][0]:                      # UVMap 3
                #     write_float16(wmb_file, val)
                writeUV.write(wmb_file, vertexExData[1][0])
                # for val in vertexExData[1][1]:                      # UVMap 4
                #     write_float16(wmb_file, val)
                writeUV.write(wmb_file, vertexExData[1][1])

        for index in vertexGroup.indexes:                           # indexes
            if wmb4:
                write_uInt16(wmb_file, index)
            else:
                write_uInt32(wmb_file, index)
        
