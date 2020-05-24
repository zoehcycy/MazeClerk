dir = 'Experiment_Data/new';
files = natsortfiles(filename_scan(dir));
%% Getting the IDs for in-testing mice
Mouse_Dict = readtable(files{2}); % Remember to delete rows starting with NaN
Lumped = readtable(files{1});
Testing_ID = Mouse_Dict.MouseID(intersect(1:length(Mouse_Dict.MouseID),find(strcmp(Mouse_Dict.ExperimentalStatus,'Testing'))));
% Change the order of Testing_ID elements to match the groups
%% Create a struct including all testing mice and updated DoBs and TaskDurations
Individual_Data = struct;
for i = 1:length(Testing_ID)
    id = Testing_ID(i);
    Lumped_indices = find(Lumped.MouseID==id);
    Mouse_Dict_index = find(Mouse_Dict.MouseID==id);
    Age = between(datetime(Mouse_Dict.DOB(Mouse_Dict_index),'InputFormat','MM/dd/yyyy'),datetime(Lumped.Date(Lumped_indices),'InputFormat','yyyy-MM-dd'),'weeks');
    [h,m,s] = hms(datetime(Lumped.VideoLength(Lumped_indices),'InputFormat','H:mm:ss'));
    Duration = m*60+s;
    id_new = ['N' num2str(id)];
    Individual_Data.(id_new) = table(Age,Duration,Lumped.Weight(Lumped_indices),Lumped.ReferenceMemoryErrors(Lumped_indices),Lumped.WorkingMemoryErrors(Lumped_indices),Lumped.Distance(Lumped_indices),Lumped.avg_velocity(Lumped_indices),Lumped.peak_velocity(Lumped_indices),'VariableNames',{'Age','Duration','Weight','RME','WME','Distance','Avg_velocity','Max_velocity'});
    Individual_Data.(id_new) = [Individual_Data.(id_new) Lumped(Lumped_indices,[4 21:29])];
end
%% Grouping
GeneID = {'H';'AD';'Crossed(H)';'Crossed(L)'};
GeneMouse = {intersect(Testing_ID,Mouse_Dict.MouseID(find(strcmp(Mouse_Dict.Genotype,'ThCre'))));intersect(Testing_ID,Mouse_Dict.MouseID(find(strcmp(Mouse_Dict.Genotype,'Tg-SwDI'))));intersect(Testing_ID,Mouse_Dict.MouseID(find(strcmp(Mouse_Dict.Genotype,'Tg-SwDI x ThCre')&strcmp(Mouse_Dict.PharmacologicalGroup,'High Dose CNO'))));intersect(Testing_ID,Mouse_Dict.MouseID(find(strcmp(Mouse_Dict.Genotype,'Tg-SwDI x ThCre')&strcmp(Mouse_Dict.PharmacologicalGroup,'Low Dose CNO'))))};
GeneGroup = table(GeneID,GeneMouse,'VariableNames',{'GroupID','MouseID'});
ExpID = {'HC';'DC';'H';'L'};
ExpMouse = {intersect(Testing_ID,Mouse_Dict.MouseID(find(strcmp(Mouse_Dict.ExperimentalGroup,'Healthy Control'))));intersect(Testing_ID,Mouse_Dict.MouseID(find(strcmp(Mouse_Dict.ExperimentalGroup,'Disease Control'))));intersect(Testing_ID,Mouse_Dict.MouseID(find(strcmp(Mouse_Dict.ExperimentalGroup,'High Dose CNO'))));intersect(Testing_ID,Mouse_Dict.MouseID(find(strcmp(Mouse_Dict.ExperimentalGroup,'Low Dose CNO'))))};
ExpGroup = table(ExpID,ExpMouse,'VariableNames',{'GroupID','MouseID'});
%% plot the range of ages of all animals in those training sessions
RangeAge = [];
stpsz = 50;
for i = 1:length(Testing_ID)
    if ismember(Testing_ID(i),GeneGroup.MouseID{1})
        m = '-';
    elseif ismember(Testing_ID(i),GeneGroup.MouseID{2}) 
        m = ':';
    elseif ismember(Testing_ID(i),GeneGroup.MouseID{3})
        m = '-.';
    elseif ismember(Testing_ID(i),GeneGroup.MouseID{4})
        m = '--';
    end
    id = ['N' num2str(Testing_ID(i))];
    if size(Individual_Data.(id),1)==0
        RangeAge(end+1,:) = [Testing_ID(i) NaN NaN];
        continue;
    end
    x = split(Individual_Data.(id).Age,'weeks');
    RangeAge(end+1,:) = [Testing_ID(i) min(x) max(x)];
    y1 = Individual_Data.(id).Duration/20; % Scaling
    y2 = Individual_Data.(id).RME;
    y3 = Individual_Data.(id).WME;
    y4 = Individual_Data.(id).Distance/600; % Scaling 
    plot(x,y1+(i-1)*stpsz,'Color','b','LineStyle',m,'LineWidth',1)
    hold on
    plot(x,y2+(i-1)*stpsz,'Color','r','LineStyle',m,'LineWidth',1)
    hold on
    plot(x,y3+(i-1)*stpsz,'Color','g','LineStyle',m,'LineWidth',1)
    hold on
    plot(x,y4+(i-1)*stpsz,'Color','k','LineStyle',m,'LineWidth',1)
end

MIN = min(RangeAge(:,2));
MAX = max(RangeAge(:,3));
Duration = NaN([47 MAX]);
RME = NaN([47 MAX]);
WME = NaN([47 MAX]);
Distance = NaN([47 MAX]);
for i = 1:length(Testing_ID)
    id = ['N' num2str(Testing_ID(i))];
    if isnan(RangeAge(i,2))
        Duration(i,:) = NaN([1 MAX]);
        continue;
    end
    Duration(i,split(Individual_Data.(id).Age,'weeks')) = Individual_Data.(id).Duration;
    RME(i,split(Individual_Data.(id).Age,'weeks')) = Individual_Data.(id).RME;
    WME(i,split(Individual_Data.(id).Age,'weeks')) = Individual_Data.(id).WME;
    Distance(i,split(Individual_Data.(id).Age,'weeks')) = Individual_Data.(id).Distance;
end
Duration(:,1:(MIN-1)) = [];
RME(:,1:(MIN-1)) = [];
WME(:,1:(MIN-1)) = [];
Distance(:,1:(MIN-1)) = [];

%% Uniform-scale line plot for GeneGroup 
x = MIN:MAX;
i = 3
% ith ID in GeneGroup
plot(x,nanmean(Duration(ismember(Testing_ID,GeneGroup.MouseID{i}),:))/20,'-og','MarkerSize',3)
hold on
% errorbar(x,nanmean(Duration(ismember(Testing_ID,GeneGroup.MouseID{i}),:))/20,nanstd(Duration(ismember(Testing_ID,GeneGroup.MouseID{i}),:))/20/sqrt(length(GeneGroup.MouseID{i})),'linestyle', 'none', 'linewidth', 1, 'color','g')
% hold on
plot(x,nanmean(RME(ismember(Testing_ID,GeneGroup.MouseID{i}),:)),'-or','MarkerSize',3)
hold on
% errorbar(x,nanmean(RME(ismember(Testing_ID,GeneGroup.MouseID{i}),:)),nanstd(RME(ismember(Testing_ID,GeneGroup.MouseID{i}),:))/sqrt(length(GeneGroup.MouseID{i})),'linestyle', 'none', 'linewidth', 1, 'color','r')
% hold on
plot(x,nanmean(WME(ismember(Testing_ID,GeneGroup.MouseID{i}),:)),'-ob','MarkerSize',3)
hold on
% errorbar(x,nanmean(WME(ismember(Testing_ID,GeneGroup.MouseID{i}),:)),nanstd(WME(ismember(Testing_ID,GeneGroup.MouseID{i}),:))/sqrt(length(GeneGroup.MouseID{i})),'linestyle', 'none', 'linewidth', 1, 'color','b')
% hold on
plot(x,nanmean(Distance(ismember(Testing_ID,GeneGroup.MouseID{i}),:))/500,'-ok','MarkerSize',3)
hold on
%errorbar(x,nanmean(Distance(ismember(Testing_ID,GeneGroup.MouseID{i}),:))/500,nanstd(Distance(ismember(Testing_ID,GeneGroup.MouseID{i}),:))/500/sqrt(length(GeneGroup.MouseID{i})),'linestyle', 'none', 'linewidth', 1, 'color','k')


%% Heatmap
y = {};
x = {};
for i = 1:size(Duration,1)
    y{end+1} = ['N' num2str(Testing_ID(i))];
end
for i = 1:size(Duration,2)
    x{end+1} = num2str(5+i);
end
h = heatmap(x,y,Distance)
h.Colormap = flipud(autumn)
h.GridVisible = 'off'
h.MissingDataColor = [1 1 1]
h.FontSize = 9
h.CellLabelColor = 'None'
h.xlabel('Age (wks)')
h.ylabel('Mouse ID')
h.Title = 'Distance Dynamics across Animals'
%% Separate line plot per AGE for GeneGroup/ExpGroup 
x = MIN:MAX;
i = 4
Group = ExpGroup;
% ith ID in GeneGroup/ExpGroup
plot(x,nanmean(Duration(ismember(Testing_ID,Group.MouseID{i}),:))/20,'-og','MarkerSize',3)
hold on
errorbar(x,nanmean(Duration(ismember(Testing_ID,Group.MouseID{i}),:))/20,nanstd(Duration(ismember(Testing_ID,Group.MouseID{i}),:))/20/sqrt(length(Group.MouseID{i})),'linestyle', 'none', 'linewidth', 1, 'color','g')
hold on
plot(x,nanmean(RME(ismember(Testing_ID,Group.MouseID{i}),:)),'-or','MarkerSize',3)
hold on
errorbar(x,nanmean(RME(ismember(Testing_ID,Group.MouseID{i}),:)),nanstd(RME(ismember(Testing_ID,Group.MouseID{i}),:))/sqrt(length(Group.MouseID{i})),'linestyle', 'none', 'linewidth', 1, 'color','r')
hold on
plot(x,nanmean(WME(ismember(Testing_ID,Group.MouseID{i}),:)),'-ob','MarkerSize',3)
hold on
errorbar(x,nanmean(WME(ismember(Testing_ID,Group.MouseID{i}),:)),nanstd(WME(ismember(Testing_ID,Group.MouseID{i}),:))/sqrt(length(Group.MouseID{i})),'linestyle', 'none', 'linewidth', 1, 'color','b')
hold on
plot(x,nanmean(Distance(ismember(Testing_ID,Group.MouseID{i}),:))/500,'-ok','MarkerSize',3)
hold on
errorbar(x,nanmean(Distance(ismember(Testing_ID,Group.MouseID{i}),:))/500,nanstd(Distance(ismember(Testing_ID,Group.MouseID{i}),:))/500/sqrt(length(Group.MouseID{i})),'linestyle', 'none', 'linewidth', 1, 'color','k')

%% Separate line plot per ConsecUTIVE SESSIONS for GeneGroup/ExpGroup 
NumofSessions = [];
for i = 1:length(Testing_ID)
    id = ['N' num2str(Testing_ID(i))];
    NumofSessions(end+1) = size(Individual_Data.(id),1);
end
MAX_Num = max(NumofSessions); % Create a mask for maximum consecutive training sessions
ConsecDuration = [];
ConsecRME = [];
ConsecWME = [];
ConsecDistance = [];
for i = 1:length(Testing_ID)
    id = ['N' num2str(Testing_ID(i))];
    if size(Individual_Data.(id),1)==0
        ConsecDuration(end+1,:) = NaN([1 MAX_Num]);
        ConsecRME(end+1,:) = NaN([1 MAX_Num]);
        ConsecWME(end+1,:) = NaN([1 MAX_Num]);
        ConsecDistance(end+1,:) = NaN([1 MAX_Num]);
        continue;
    end
    ConsecDuration(end+1,:) = [Individual_Data.(id).Duration' NaN([1 MAX_Num-size(Individual_Data.(id),1)])];
    ConsecRME(end+1,:) = [Individual_Data.(id).RME' NaN([1 MAX_Num-size(Individual_Data.(id),1)])];
    ConsecWME(end+1,:) = [Individual_Data.(id).WME' NaN([1 MAX_Num-size(Individual_Data.(id),1)])];
    ConsecDistance(end+1,:) = [Individual_Data.(id).Distance' NaN([1 MAX_Num-size(Individual_Data.(id),1)])];
end
    
x = 1:MAX_Num;
i = 4
Group = ExpGroup;
% ith ID in GeneGroup/ExpGroup
plot(x,nanmean(ConsecDuration(ismember(Testing_ID,Group.MouseID{i}),:))/20,'-og','MarkerSize',3)
hold on
errorbar(x,nanmean(ConsecDuration(ismember(Testing_ID,Group.MouseID{i}),:))/20,nanstd(ConsecDuration(ismember(Testing_ID,Group.MouseID{i}),:))/20/sqrt(length(Group.MouseID{i})),'linestyle', 'none', 'linewidth', 1, 'color','g')
hold on
plot(x,nanmean(ConsecRME(ismember(Testing_ID,Group.MouseID{i}),:)),'-or','MarkerSize',3)
hold on
errorbar(x,nanmean(ConsecRME(ismember(Testing_ID,Group.MouseID{i}),:)),nanstd(ConsecRME(ismember(Testing_ID,Group.MouseID{i}),:))/sqrt(length(Group.MouseID{i})),'linestyle', 'none', 'linewidth', 1, 'color','r')
hold on
plot(x,nanmean(ConsecWME(ismember(Testing_ID,Group.MouseID{i}),:)),'-ob','MarkerSize',3)
hold on
errorbar(x,nanmean(ConsecWME(ismember(Testing_ID,Group.MouseID{i}),:)),nanstd(ConsecWME(ismember(Testing_ID,Group.MouseID{i}),:))/sqrt(length(Group.MouseID{i})),'linestyle', 'none', 'linewidth', 1, 'color','b')
hold on
plot(x,nanmean(ConsecDistance(ismember(Testing_ID,Group.MouseID{i}),:))/500,'-ok','MarkerSize',3)
hold on
errorbar(x,nanmean(ConsecDistance(ismember(Testing_ID,Group.MouseID{i}),:))/500,nanstd(ConsecDistance(ismember(Testing_ID,Group.MouseID{i}),:))/500/sqrt(length(Group.MouseID{i})),'linestyle', 'none', 'linewidth', 1, 'color','k')






    