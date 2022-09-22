import numpy as np
import pickle
import pandas as pd
import glob
import os
import nibabel as nib

def render(index_list,out_values,atlas,outvolume_size,outname):
    atlas_data = atlas.get_fdata()
    outvolume = outvolume_size
    for i,roi in enumerate(index_list):
        roi_index = np.where(atlas_data==roi+1)
        outvolume[roi_index] = out_values[i]
    outimage = nib.Nifti1Image(outvolume, affine=atlas.affine)
    nib.save(outimage,outname)
    outimage.uncache()


def brainrenders(group,tau_mean):
    if 'dhcp' in group:
        ## Load templates and set outvolume size
        atlas = nib.load('/dhcp/fmri_anna_graham/dhcp_hcp_timescales/data/schaefer_40weeks.nii.gz')
        outvolume_size = np.zeros((202, 274, 217))
    else:
        atlas  = nib.load('/dhcp/fmri_anna_graham/dhcp_hcp_timescales/data/Schaefer2018_400Parcels_17Networks_order_FSLMNI152_2mm.nii.gz')
        outvolume_size = np.zeros((91, 109, 91))

    atlas_data = atlas.get_fdata()

    ##### TAU distribution visualisation    
    print(f'Working on tau render for {group}....')
    render(range(0,tau_mean.shape[0]),tau_mean,atlas,outvolume_size,f"/dhcp/fmri_anna_graham/dhcp_hcp_timescales/results/{group}_tauvalues_render.nii.gz")

    ##### ROI visualisation and grouping

    ## Load ROI label file
    print(f'Working on roi renders....')
    network_file17 = pd.read_csv('/dhcp/fmri_anna_graham/dhcp_hcp_timescales/data/Schaefer2018_400Parcels_17Networks_order.txt',sep = '\t', header = None)
    roi_names_all = np.array(network_file17[1])

    ## Get indexes and names of unimodal vs transmodal rois + make brain render file. INCLUDED LOW SNR REGIONS
    with open('/dhcp/fmri_anna_graham/dhcp_hcp_timescales/data/roi_by_netclass.pickle','rb') as f:
        network_file = pickle.load(f)
    unimodal_index = [i-1 for i in network_file['unimodal']]
    transmodal_index = [i-1 for i in network_file['transmodal']]
    roi_value = np.concatenate((np.repeat(1,len(unimodal_index)),np.repeat(2,len(transmodal_index))))
    uni_vs_trans_index = unimodal_index + transmodal_index
    render(uni_vs_trans_index,roi_value,atlas, outvolume_size,f"/dhcp/fmri_anna_graham/dhcp_hcp_timescales/results/{group}_uni_vs_transmodal_render_all.nii.gz")

    ## Get indexes and names of 8 networks + make brain render file unique for all nets.
    net8 = np.unique(np.array([i.split('_')[2][0:3] for i in roi_names_all]))
    myorder = [4,5,3,0,1,2,6,7]
    net8 = [net8[i] for i in myorder]
    tem_index = [i for i, v in enumerate(net8) if 'Tem' in v]
    net8[6] = 'TempPar'
    net_idx = []
    netnum_list = []
    print(net8)
    for netnum,net in enumerate(net8):
        for i,roi in enumerate(roi_names_all):
            if net in roi:
                net_idx.append(i)
                netnum_list.append(netnum+1)
    render(net_idx,netnum_list,atlas,outvolume_size,f"/dhcp/fmri_anna_graham/dhcp_hcp_timescales/results/{group}_8networks_render.nii.gz")
