// src/components/role/PermissionSelector.jsx
import React, { useState } from 'react';
import { PERMISSIONS } from '../../utils/constants';
import { IoChevronDown, IoChevronRight } from 'react-icons/io5';

function PermissionSelector({ permissions, onChange }) {
  const [expandedSections, setExpandedSections] = useState({
    general: true,
    text: true,
    voice: true,
    moderation: true,
  });

  const toggleSection = (section) => {
    setExpandedSections(prev => ({ ...prev, [section]: !prev[section] }));
  };

  const permissionSections = {
    general: [
      { name: 'VIEW_CHANNEL', label: 'View Channel', value: PERMISSIONS.VIEW_CHANNEL },
      { name: 'CREATE_INVITE', label: 'Create Invite', value: PERMISSIONS.CREATE_INVITE },
      { name: 'CHANGE_NICKNAME', label: 'Change Nickname', value: PERMISSIONS.CHANGE_NICKNAME },
      { name: 'MANAGE_NICKNAMES', label: 'Manage Nicknames', value: PERMISSIONS.MANAGE_NICKNAMES },
    ],
    text: [
      { name: 'SEND_MESSAGES', label: 'Send Messages', value: PERMISSIONS.SEND_MESSAGES },
      { name: 'READ_MESSAGE_HISTORY', label: 'Read Message History', value: PERMISSIONS.READ_MESSAGE_HISTORY },
      { name: 'MANAGE_MESSAGES', label: 'Manage Messages', value: PERMISSIONS.MANAGE_MESSAGES },
      { name: 'ADD_REACTIONS', label: 'Add Reactions', value: PERMISSIONS.ADD_REACTIONS },
      { name: 'ATTACH_FILES', label: 'Attach Files', value: PERMISSIONS.ATTACH_FILES },
      { name: 'EMBED_LINKS', label: 'Embed Links', value: PERMISSIONS.EMBED_LINKS },
      { name: 'MENTION_EVERYONE', label: 'Mention @everyone', value: PERMISSIONS.MENTION_EVERYONE },
      { name: 'USE_EXTERNAL_EMOJIS', label: 'Use External Emojis', value: PERMISSIONS.USE_EXTERNAL_EMOJIS },
    ],
    voice: [
      { name: 'CONNECT', label: 'Connect', value: PERMISSIONS.CONNECT },
      { name: 'SPEAK', label: 'Speak', value: PERMISSIONS.SPEAK },
      { name: 'MUTE_MEMBERS', label: 'Mute Members', value: PERMISSIONS.MUTE_MEMBERS },
      { name: 'DEAFEN_MEMBERS', label: 'Deafen Members', value: PERMISSIONS.DEAFEN_MEMBERS },
      { name: 'MOVE_MEMBERS', label: 'Move Members', value: PERMISSIONS.MOVE_MEMBERS },
      { name: 'USE_VAD', label: 'Use Voice Activity', value: PERMISSIONS.USE_VAD },
    ],
    moderation: [
      { name: 'MANAGE_CHANNELS', label: 'Manage Channels', value: PERMISSIONS.MANAGE_CHANNELS },
      { name: 'MANAGE_GUILD', label: 'Manage Server', value: PERMISSIONS.MANAGE_GUILD },
      { name: 'MANAGE_ROLES', label: 'Manage Roles', value: PERMISSIONS.MANAGE_ROLES },
      { name: 'KICK_MEMBERS', label: 'Kick Members', value: PERMISSIONS.KICK_MEMBERS },
      { name: 'BAN_MEMBERS', label: 'Ban Members', value: PERMISSIONS.BAN_MEMBERS },
      { name: 'VIEW_AUDIT_LOG', label: 'View Audit Log', value: PERMISSIONS.VIEW_AUDIT_LOG },
      { name: 'MANAGE_WEBHOOKS', label: 'Manage Webhooks', value: PERMISSIONS.MANAGE_WEBHOOKS },
      { name: 'MANAGE_EMOJIS', label: 'Manage Emojis', value: PERMISSIONS.MANAGE_EMOJIS },
    ],
  };

  const handleToggle = (permissionValue) => {
    if (permissions & permissionValue) {
      onChange(permissions & ~permissionValue);
    } else {
      onChange(permissions | permissionValue);
    }
  };

  const toggleAllInSection = (section, value) => {
    let newPermissions = permissions;
    section.forEach(perm => {
      if (value) {
        newPermissions |= perm.value;
      } else {
        newPermissions &= ~perm.value;
      }
    });
    onChange(newPermissions);
  };

  const isAllSelected = (section) => {
    return section.every(perm => permissions & perm.value);
  };

  const isAnySelected = (section) => {
    return section.some(perm => permissions & perm.value);
  };

  const renderSection = (title, sectionKey, permissionsList) => (
    <div className="mb-4 border border-[#202225] rounded-lg overflow-hidden">
      <button
        type="button"
        onClick={() => toggleSection(sectionKey)}
        className="w-full flex items-center justify-between p-3 bg-[#202225] hover:bg-[#1a1c1f] transition-colors"
      >
        <span className="text-white font-semibold">{title}</span>
        <div className="flex items-center space-x-3">
          {isAnySelected(permissionsList) && (
            <span className="text-xs text-[#5865f2]">●</span>
          )}
          {expandedSections[sectionKey] ? <IoChevronDown /> : <IoChevronRight />}
        </div>
      </button>
      
      {expandedSections[sectionKey] && (
        <div className="p-3 space-y-2">
          <button
            type="button"
            onClick={() => toggleAllInSection(permissionsList, !isAllSelected(permissionsList))}
            className="text-xs text-[#5865f2] hover:underline mb-2"
          >
            {isAllSelected(permissionsList) ? 'Deselect All' : 'Select All'}
          </button>
          {permissionsList.map((perm) => (
            <label key={perm.name} className="flex items-center cursor-pointer">
              <input
                type="checkbox"
                checked={(permissions & perm.value) === perm.value}
                onChange={() => handleToggle(perm.value)}
                className="mr-3"
              />
              <span className="text-[#b9bbbe] text-sm">{perm.label}</span>
            </label>
          ))}
        </div>
      )}
    </div>
  );

  return (
    <div className="bg-[#202225] rounded-lg p-4 max-h-96 overflow-y-auto">
      {renderSection('General', 'general', permissionSections.general)}
      {renderSection('Text Permissions', 'text', permissionSections.text)}
      {renderSection('Voice Permissions', 'voice', permissionSections.voice)}
      {renderSection('Moderation', 'moderation', permissionSections.moderation)}
      
      <div className="mt-4 p-3 bg-[#1a1c1f] rounded-lg">
        <label className="flex items-center cursor-pointer">
          <input
            type="checkbox"
            checked={(permissions & PERMISSIONS.ADMINISTRATOR) === PERMISSIONS.ADMINISTRATOR}
            onChange={() => handleToggle(PERMISSIONS.ADMINISTRATOR)}
            className="mr-3"
          />
          <div>
            <span className="text-white font-semibold">Administrator</span>
            <p className="text-[#72767d] text-xs">Grants all permissions and bypasses all permission checks</p>
          </div>
        </label>
      </div>
    </div>
  );
}

export default PermissionSelector;