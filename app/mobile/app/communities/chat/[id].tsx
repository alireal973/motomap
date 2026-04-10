import React, { useState, useEffect, useRef, useCallback } from "react";
import {
  View,
  Text,
  StyleSheet,
  FlatList,
  TouchableOpacity,
  TextInput,
  KeyboardAvoidingView,
  Platform,
  ActivityIndicator,
  Image,
} from "react-native";
import { useLocalSearchParams, router } from "expo-router";
import { SafeAreaView } from "react-native-safe-area-context";
import { Ionicons } from "@expo/vector-icons";
import { colors, spacing, radius, typography, shadows } from "../../../theme";
import GlassCard from "../../../components/GlassCard";
import { useAuth } from "../../../context/AuthContext";

interface ChatMessage {
  id: string;
  sender: {
    id: string;
    username: string;
    avatar_url?: string;
  };
  content: string;
  timestamp: string;
  is_mine: boolean;
}

interface CommunityInfo {
  id: string;
  name: string;
  member_count: number;
  online_count: number;
}

export default function CommunityChatScreen() {
  const { id } = useLocalSearchParams<{ id: string }>();
  const { user } = useAuth();
  const flatListRef = useRef<FlatList>(null);

  const [community, setCommunity] = useState<CommunityInfo | null>(null);
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [newMessage, setNewMessage] = useState("");
  const [loading, setLoading] = useState(true);
  const [sending, setSending] = useState(false);
  const [isConnected, setIsConnected] = useState(true);

  useEffect(() => {
    initializeChat();
    return () => {
      // Cleanup WebSocket connection
    };
  }, [id]);

  const initializeChat = async () => {
    try {
      // TODO: Initialize WebSocket connection and fetch history
      setTimeout(() => {
        setCommunity({
          id: id || "1",
          name: "İstanbul Motorcuları",
          member_count: 1245,
          online_count: 47,
        });

        setMessages([
          {
            id: "m1",
            sender: { id: "u1", username: "rider34" },
            content: "Selam arkadaşlar, bugün harika bir sürüş yaptık!",
            timestamp: "2024-01-20T10:00:00Z",
            is_mine: false,
          },
          {
            id: "m2",
            sender: { id: "u2", username: "motosever" },
            content: "Nerelere gittiniz?",
            timestamp: "2024-01-20T10:01:00Z",
            is_mine: false,
          },
          {
            id: "m3",
            sender: { id: "u1", username: "rider34" },
            content: "Belgrad Ormanı'ndan Kilyos'a. Yol süperdi, trafik de yoktu.",
            timestamp: "2024-01-20T10:02:00Z",
            is_mine: false,
          },
          {
            id: "m4",
            sender: { id: "me", username: user?.username || "Ben" },
            content: "Ben de geçen hafta gittim oraya, bayıldım! 🏍️",
            timestamp: "2024-01-20T10:03:00Z",
            is_mine: true,
          },
          {
            id: "m5",
            sender: { id: "u3", username: "touring_pro" },
            content: "Hafta sonu Bolu turu var, katılmak isteyen var mı?",
            timestamp: "2024-01-20T10:05:00Z",
            is_mine: false,
          },
          {
            id: "m6",
            sender: { id: "u4", username: "adventurerider" },
            content: "Ben varım! Kaç kişi olacağız?",
            timestamp: "2024-01-20T10:06:00Z",
            is_mine: false,
          },
          {
            id: "m7",
            sender: { id: "u3", username: "touring_pro" },
            content: "Şu an 8 kişiyiz, hedef 15 kişi. Detayları forum'a yazdım.",
            timestamp: "2024-01-20T10:07:00Z",
            is_mine: false,
          },
        ]);

        setLoading(false);
      }, 500);
    } catch (error) {
      console.error("Chat initialization error:", error);
      setLoading(false);
    }
  };

  const handleSendMessage = async () => {
    if (!newMessage.trim()) return;
    setSending(true);

    const tempMessage: ChatMessage = {
      id: `temp_${Date.now()}`,
      sender: {
        id: user?.id || "me",
        username: user?.username || "Ben",
      },
      content: newMessage.trim(),
      timestamp: new Date().toISOString(),
      is_mine: true,
    };

    setMessages((prev) => [...prev, tempMessage]);
    setNewMessage("");

    try {
      // TODO: Send via WebSocket
      // websocket.send({ type: 'message', content: newMessage });
    } catch (error) {
      console.error("Send message error:", error);
    } finally {
      setSending(false);
      setTimeout(() => {
        flatListRef.current?.scrollToEnd({ animated: true });
      }, 100);
    }
  };

  const formatTime = (dateStr: string): string => {
    const date = new Date(dateStr);
    return date.toLocaleTimeString("tr-TR", { hour: "2-digit", minute: "2-digit" });
  };

  const formatDateSeparator = (dateStr: string): string => {
    const date = new Date(dateStr);
    const today = new Date();
    const yesterday = new Date(today);
    yesterday.setDate(yesterday.getDate() - 1);

    if (date.toDateString() === today.toDateString()) {
      return "Bugün";
    } else if (date.toDateString() === yesterday.toDateString()) {
      return "Dün";
    }
    return date.toLocaleDateString("tr-TR", { day: "numeric", month: "long" });
  };

  const renderMessage = useCallback(
    ({ item, index }: { item: ChatMessage; index: number }) => {
      const showDateSeparator =
        index === 0 ||
        new Date(messages[index - 1].timestamp).toDateString() !==
          new Date(item.timestamp).toDateString();

      const showAvatar =
        !item.is_mine &&
        (index === messages.length - 1 || messages[index + 1]?.sender.id !== item.sender.id);

      return (
        <View>
          {showDateSeparator && (
            <View style={styles.dateSeparator}>
              <Text style={styles.dateSeparatorText}>{formatDateSeparator(item.timestamp)}</Text>
            </View>
          )}

          <View style={[styles.messageRow, item.is_mine && styles.myMessageRow]}>
            {!item.is_mine && (
              <View style={styles.avatarContainer}>
                {showAvatar ? (
                  <View style={styles.avatar}>
                    {item.sender.avatar_url ? (
                      <Image source={{ uri: item.sender.avatar_url }} style={styles.avatarImage} />
                    ) : (
                      <Text style={styles.avatarText}>
                        {item.sender.username.charAt(0).toUpperCase()}
                      </Text>
                    )}
                  </View>
                ) : (
                  <View style={styles.avatarPlaceholder} />
                )}
              </View>
            )}

            <View style={[styles.messageBubble, item.is_mine && styles.myMessageBubble]}>
              {!item.is_mine && showAvatar && (
                <Text style={styles.senderName}>{item.sender.username}</Text>
              )}
              <Text style={[styles.messageText, item.is_mine && styles.myMessageText]}>
                {item.content}
              </Text>
              <Text style={[styles.messageTime, item.is_mine && styles.myMessageTime]}>
                {formatTime(item.timestamp)}
              </Text>
            </View>
          </View>
        </View>
      );
    },
    [messages]
  );

  if (loading) {
    return (
      <SafeAreaView style={styles.container}>
        <View style={styles.loadingContainer}>
          <ActivityIndicator size="large" color={colors.accentBlue} />
        </View>
      </SafeAreaView>
    );
  }

  return (
    <SafeAreaView style={styles.container} edges={["top"]}>
      {/* Header */}
      <View style={styles.header}>
        <TouchableOpacity onPress={() => router.back()} style={styles.headerButton}>
          <Ionicons name="arrow-back" size={24} color={colors.textPrimary} />
        </TouchableOpacity>

        <TouchableOpacity
          style={styles.headerTitle}
          onPress={() => router.push(`/communities/${id}` as any)}
        >
          <Text style={styles.communityName} numberOfLines={1}>
            {community?.name}
          </Text>
          <View style={styles.onlineStatus}>
            <View style={[styles.onlineDot, isConnected && styles.onlineDotActive]} />
            <Text style={styles.onlineText}>
              {community?.online_count} çevrimiçi / {community?.member_count} üye
            </Text>
          </View>
        </TouchableOpacity>

        <TouchableOpacity style={styles.headerButton}>
          <Ionicons name="ellipsis-vertical" size={24} color={colors.textPrimary} />
        </TouchableOpacity>
      </View>

      {/* Messages */}
      <KeyboardAvoidingView
        style={styles.flex}
        behavior={Platform.OS === "ios" ? "padding" : undefined}
        keyboardVerticalOffset={0}
      >
        <FlatList
          ref={flatListRef}
          data={messages}
          renderItem={renderMessage}
          keyExtractor={(item) => item.id}
          contentContainerStyle={styles.messageList}
          showsVerticalScrollIndicator={false}
          onContentSizeChange={() => {
            flatListRef.current?.scrollToEnd({ animated: false });
          }}
        />

        {/* Connection Status */}
        {!isConnected && (
          <View style={styles.connectionWarning}>
            <Ionicons name="cloud-offline-outline" size={16} color={colors.warningYellow} />
            <Text style={styles.connectionWarningText}>Bağlantı kuruluyor...</Text>
          </View>
        )}

        {/* Input */}
        <View style={styles.inputContainer}>
          <TouchableOpacity style={styles.attachButton}>
            <Ionicons name="add-circle-outline" size={28} color={colors.textSecondary} />
          </TouchableOpacity>

          <TextInput
            style={styles.input}
            placeholder="Mesaj yaz..."
            placeholderTextColor={colors.textMuted}
            value={newMessage}
            onChangeText={setNewMessage}
            multiline
            maxLength={1000}
          />

          {newMessage.trim() ? (
            <TouchableOpacity style={styles.sendButton} onPress={handleSendMessage} disabled={sending}>
              {sending ? (
                <ActivityIndicator size="small" color={colors.textPrimary} />
              ) : (
                <Ionicons name="send" size={22} color={colors.textPrimary} />
              )}
            </TouchableOpacity>
          ) : (
            <TouchableOpacity style={styles.emojiButton}>
              <Ionicons name="happy-outline" size={28} color={colors.textSecondary} />
            </TouchableOpacity>
          )}
        </View>
      </KeyboardAvoidingView>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: colors.bgPrimary,
  },
  flex: {
    flex: 1,
  },
  loadingContainer: {
    flex: 1,
    justifyContent: "center",
    alignItems: "center",
  },
  header: {
    flexDirection: "row",
    alignItems: "center",
    paddingHorizontal: spacing.sm,
    paddingVertical: spacing.sm,
    borderBottomWidth: 1,
    borderBottomColor: colors.borderDefault,
  },
  headerButton: {
    padding: spacing.sm,
  },
  headerTitle: {
    flex: 1,
    marginHorizontal: spacing.sm,
  },
  communityName: {
    ...typography.body,
    color: colors.textPrimary,
    fontWeight: "600",
  },
  onlineStatus: {
    flexDirection: "row",
    alignItems: "center",
    marginTop: 2,
  },
  onlineDot: {
    width: 8,
    height: 8,
    borderRadius: 4,
    backgroundColor: colors.textMuted,
    marginRight: spacing.xs,
  },
  onlineDotActive: {
    backgroundColor: "#4CAF50",
  },
  onlineText: {
    ...typography.caption,
    color: colors.textSecondary,
  },
  messageList: {
    padding: spacing.md,
  },
  dateSeparator: {
    alignItems: "center",
    marginVertical: spacing.md,
  },
  dateSeparatorText: {
    ...typography.caption,
    color: colors.textMuted,
    backgroundColor: colors.surfaceGlass,
    paddingHorizontal: spacing.md,
    paddingVertical: spacing.xs,
    borderRadius: radius.full,
  },
  messageRow: {
    flexDirection: "row",
    marginBottom: spacing.xs,
    maxWidth: "85%",
  },
  myMessageRow: {
    alignSelf: "flex-end",
    flexDirection: "row-reverse",
  },
  avatarContainer: {
    marginRight: spacing.sm,
  },
  avatar: {
    width: 32,
    height: 32,
    borderRadius: 16,
    backgroundColor: colors.surfaceGlass,
    justifyContent: "center",
    alignItems: "center",
  },
  avatarImage: {
    width: 32,
    height: 32,
    borderRadius: 16,
  },
  avatarText: {
    ...typography.bodySmall,
    color: colors.accentBlue,
    fontWeight: "600",
  },
  avatarPlaceholder: {
    width: 32,
  },
  messageBubble: {
    backgroundColor: colors.surfaceGlass,
    paddingHorizontal: spacing.md,
    paddingVertical: spacing.sm,
    borderRadius: radius.lg,
    borderTopLeftRadius: radius.xs,
    maxWidth: "100%",
  },
  myMessageBubble: {
    backgroundColor: colors.accentBlue,
    borderTopLeftRadius: radius.lg,
    borderTopRightRadius: radius.xs,
  },
  senderName: {
    ...typography.caption,
    color: colors.accentBlue,
    fontWeight: "600",
    marginBottom: 2,
  },
  messageText: {
    ...typography.body,
    color: colors.textPrimary,
  },
  myMessageText: {
    color: colors.textPrimary,
  },
  messageTime: {
    ...typography.caption,
    color: colors.textMuted,
    alignSelf: "flex-end",
    marginTop: 2,
  },
  myMessageTime: {
    color: "rgba(255, 255, 255, 0.7)",
  },
  connectionWarning: {
    flexDirection: "row",
    justifyContent: "center",
    alignItems: "center",
    backgroundColor: "rgba(255, 193, 7, 0.1)",
    padding: spacing.sm,
    gap: spacing.xs,
  },
  connectionWarningText: {
    ...typography.caption,
    color: colors.warningYellow,
  },
  inputContainer: {
    flexDirection: "row",
    alignItems: "flex-end",
    paddingHorizontal: spacing.sm,
    paddingVertical: spacing.sm,
    borderTopWidth: 1,
    borderTopColor: colors.borderDefault,
    backgroundColor: colors.bgPrimary,
  },
  attachButton: {
    padding: spacing.xs,
    marginRight: spacing.xs,
  },
  input: {
    flex: 1,
    backgroundColor: colors.surfaceGlass,
    borderRadius: radius.lg,
    paddingHorizontal: spacing.md,
    paddingVertical: spacing.sm,
    ...typography.body,
    color: colors.textPrimary,
    maxHeight: 100,
  },
  sendButton: {
    width: 44,
    height: 44,
    borderRadius: 22,
    backgroundColor: colors.accentBlue,
    justifyContent: "center",
    alignItems: "center",
    marginLeft: spacing.sm,
  },
  emojiButton: {
    padding: spacing.xs,
    marginLeft: spacing.xs,
  },
});
