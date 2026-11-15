% Read the authors' groundTruth objects; no original files are modified.
root = getenv('JIG_VAL');
out = getenv('JIG_CSV');
rows = cell(0,10);
for seq = 1:6
    name = sprintf('video_%d', seq);
    sub = fullfile(root,name);
    S = load(fullfile(sub,'jaw_poses_left_right.mat'));
    T = S.gTruth.LabelData;
    sources = S.gTruth.DataSource;
    assert(iscell(sources) && numel(sources)==height(T));
    assert(isequal(T.Properties.VariableNames,{'jawPoseLeft','jawPoseRight'}));
    assert(height(T)==75);
    for i = 1:height(T)
        image = regexp(char(sources{i}),'[^/\\]+$','match','once');
        assert(isfile(fullfile(sub,'images',image)));
        for side = ["Left","Right"]
            label = T.("jawPose"+side){i};
            status = 'valid';
            xy = NaN(3,2);
            if isempty(label) || (iscell(label) && numel(label)==1 && isempty(label{1}))
                status = 'empty';
            elseif ~iscell(label) || numel(label)~=1 || ~isequal(size(label{1}),[3,2]) || ~all(isfinite(label{1}),'all')
                status = 'invalid_line';
                if iscell(label) && numel(label)==1
                    fprintf('%s %s %s: %s\n',name,image,side,mat2str(size(label{1})));
                end
            else
                xy = label{1} - 1; % MATLAB pixel centers to zero-based image coordinates
            end
            rows(end+1,:) = {name,image,char(side),xy(1,1),xy(1,2),xy(2,1),xy(2,2),xy(3,1),xy(3,2),status};
        end
    end
end
writetable(cell2table(rows,'VariableNames',{'sequence','image','tool','tip1_x','tip1_y','base_x','base_y','tip2_x','tip2_y','status'}),out);
